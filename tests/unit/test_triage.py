"""DE-05: triage scoring/gates/overrides, manifest resolution with patterns, and the real configs."""

from __future__ import annotations

import copy

import pandas as pd
import pytest

from flamesafe import config
from flamesafe.ingestion import download as dl
from flamesafe.ingestion import triage as tri

BASE = {
    "weights": {"R1": 0.30, "R2": 0.15, "R3": 0.20, "R4": 0.20, "R5": 0.10, "R6": 0.05},
    "thresholds": {"tier1": 0.70, "tier2": 0.45},
    "gates": {"tier1": {"R4_min": 3, "R3_min": 2, "R5_min": 2}, "tier2": {"R3_or_R4_min": 2}},
    "investigations": {
        "PSI-1": {"scores": {"R1": 3, "R2": 3, "R3": 3, "R4": 3, "R5": 3, "R6": 3}, "justification": "top"},
        "PSI-2": {"scores": {"R1": 3, "R2": 3, "R3": 2, "R4": 2, "R5": 2, "R6": 2}, "justification": "no outcome"},
        "PSI-3": {"scores": {"R1": 3, "R2": 2, "R3": 1, "R4": 1, "R5": 1, "R6": 2}, "justification": "ranges only"},
        "PSI-4": {"scores": {"R1": 1, "R2": 1, "R3": 0, "R4": 0, "R5": 0, "R6": 1}, "justification": "metadata"},
    },
}
INV = pd.DataFrame({"psi_id": ["PSI-1", "PSI-2", "PSI-3", "PSI-4"], "acronym": ["A", "B", "C", None],
                    "project_type": ["Microgravity Investigation"] * 3 + ["Ground Investigation"],
                    "access_status": ["available"] * 4})


def test_score_formula():
    assert tri.score(BASE["investigations"]["PSI-1"]["scores"], BASE["weights"]) == 1.0
    assert tri.score(BASE["investigations"]["PSI-2"]["scores"], BASE["weights"]) == pytest.approx(0.817, abs=1e-3)


def test_gates_demote_and_record_reason():
    df = tri.compute(BASE, INV).set_index("psi_id")
    assert df.loc["PSI-1", "tier"] == 1
    assert (df.loc["PSI-2", "tier_rubric"], df.loc["PSI-2", "tier"]) == (1, 2)
    assert "gate T1: R4<3" in df.loc["PSI-2", "tier_notes"]
    assert (df.loc["PSI-3", "tier_rubric"], df.loc["PSI-3", "tier"]) == (2, 3)
    assert df.loc["PSI-4", "tier"] == 3


def test_override_requires_fields_and_wins():
    cfg = copy.deepcopy(BASE)
    cfg["investigations"]["PSI-3"]["override"] = {"tier": 2, "reason": "unique suppression context", "by": "PHY"}
    df = tri.compute(cfg, INV).set_index("psi_id")
    assert df.loc["PSI-3", "tier"] == 2 and "override PHY" in df.loc["PSI-3", "tier_notes"]
    cfg["investigations"]["PSI-3"]["override"] = {"tier": 2}
    with pytest.raises(tri.TriageError):
        tri.compute(cfg, INV)


def test_validation_catches_missing_records_and_bad_scores():
    cfg = copy.deepcopy(BASE)
    del cfg["investigations"]["PSI-4"]
    cfg["investigations"]["PSI-1"]["scores"]["R2"] = 5
    with pytest.raises(tri.TriageError) as exc:
        tri.compute(cfg, INV)
    assert "falta PSI-4" in str(exc.value) and "PSI-1" in str(exc.value)


def test_markdown_render_and_write(tmp_path):
    df = tri.compute(BASE, INV)
    doc = tmp_path / "doc.md"
    doc.write_text(f"# T\n\n{tri.AUTO_BEGIN}\nold\n{tri.AUTO_END}\n\nfooter\n", encoding="utf-8")
    tri.write_outputs(df, doc=doc, csv_path=tmp_path / "m.csv")
    text = doc.read_text(encoding="utf-8")
    assert "old" not in text and "footer" in text and "nan" not in text
    assert "— (tierra)" in text and "Tier 1: 1" in text
    assert len(pd.read_csv(tmp_path / "m.csv")) == 4


def test_manifest_patterns_resolve_and_empty_pattern_fails(tmp_path):
    d = tmp_path / "silver"
    d.mkdir()
    pd.DataFrame([{"psi_id": "PSI-1", "inventory": "added", "file_name": n, "file_bytes": 10.0}
                  for n in ("PSI-1_Raw Data_HKPData_a.csv", "PSI-1_Raw Data_HKPData_b.csv", "PSI-1_Reports_x.pdf")]
                 ).to_parquet(d / "files.parquet")
    pd.DataFrame(columns=["psi_id", "file_name", "listed_bytes"]).to_parquet(d / "experimental_tables.parquet")
    cfg = {"groups": [{"name": "g", "files": {"PSI-1": [{"pattern": r"_HKPData_.*\.csv$"}, "PSI-1_Reports_x.pdf"]}}]}
    reqs = dl.requests_from_selection(cfg, d)
    assert [r.file_name for r in reqs] == ["PSI-1_Raw Data_HKPData_a.csv", "PSI-1_Raw Data_HKPData_b.csv", "PSI-1_Reports_x.pdf"]
    assert {r.reason for r in reqs} == {"g"}
    with pytest.raises(KeyError):
        dl.requests_from_selection({"groups": [{"name": "g", "files": {"PSI-1": [{"pattern": "nomatch"}]}}]}, d)
    with pytest.raises(dl.BudgetError):
        dl.check_budget(reqs, 100, 100, max_files=2)


def test_real_triage_config_is_complete_and_consistent():
    cfg = config.load("triage")
    ids = list(cfg["investigations"])
    assert len(ids) == 24
    df = tri.compute(cfg, pd.DataFrame({"psi_id": ids, "acronym": ids, "project_type": "x", "access_status": "x"}))
    assert set(df["tier"]) <= {1, 2, 3}
    tier1 = df[df["tier"] == 1]
    assert (tier1["R4"] == 3).all() and (tier1["R5"] >= 2).all()


def test_real_manifest_stays_within_its_budget_shape():
    man = config.load("acquisition_manifest")
    b = man["budget"]
    assert b["max_total_mb"] <= 500 and b["max_files"] <= 150
    deny = set(config.load("sources")["download_budget"]["deny_extensions"])
    for g in man["groups"]:
        for entries in g["files"].values():
            for e in entries:
                name = e if isinstance(e, str) else e["pattern"]
                assert not any(name.endswith(f".{x}") or name.endswith(f"\\.{x}$") for x in deny)
