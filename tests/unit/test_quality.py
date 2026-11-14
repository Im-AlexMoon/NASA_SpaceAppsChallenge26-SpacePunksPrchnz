"""DE-09/DE-10: contracts on committed gold samples (offline, runs in CI), contract sensitivity, dictionary coverage."""

from __future__ import annotations

import shutil

import pandas as pd
import pytest

from flamesafe import config
from flamesafe.quality import validate as v
from flamesafe.quality.schemas import GOLD

SAMPLE = config.ROOT / "data" / "sample"


def sample(name: str) -> pd.DataFrame:
    return pd.read_parquet(SAMPLE / f"gold_{name}.parquet")


@pytest.mark.parametrize("name", list(GOLD))
def test_committed_samples_satisfy_gold_contracts(name):
    res = v.check_schema(sample(name), GOLD[name])
    assert res["ok"], res.get("failures")


def test_samples_cover_edge_cases():
    g = sample("gas_flame_tests")
    assert {"flash", "yes", "no"} <= set(g.ignition_outcome.dropna())
    assert {"experimental_table", "eventdata", "none"} <= set(g.outcome_source)
    assert g.qualifier.notna().any() and (g.flame_type == "inverse").any()
    d = sample("droplet_tests")
    assert d.quality_flags.notna().any() and (~d.x_co2_inferred & (d.campaign == "CFI")).any()


@pytest.mark.parametrize(("mutate", "expected_check"), [
    (lambda g: g.assign(xo2=1.5), "in_range"),
    (lambda g: g.assign(ignited=pd.array([True] * len(g), dtype="boolean")), "flash stays NULL"),
    (lambda g: pd.concat([g, g.iloc[:1]], ignore_index=True), "unique (psi_id, test_id)"),
    (lambda g: g.assign(fuel="kerosene"), "isin"),
    (lambda g: g.assign(extra_col=1), "column_in_schema"),
])
def test_gas_contract_rejects_bad_data(mutate, expected_check):
    res = v.check_schema(mutate(sample("gas_flame_tests")), GOLD["gas_flame_tests"])
    assert not res["ok"] and any(expected_check in str(f["check"]) for f in res["failures"])


def test_droplet_contract_blocks_unverified_flex_k():
    d = sample("droplet_tests")
    d.loc[d.campaign == "FLEX", "k_hot_mm2_s"] = 0.5
    res = v.check_schema(d, GOLD["droplet_tests"])
    assert not res["ok"] and any("R-DE-05b" in str(f["check"]) for f in res["failures"])


def test_documented_columns_parser():
    text = "## Silver\n### `x`\n| `a` | t |\n## Gold\n### `t1` (RQ)\n| Columna | Tipo |\n|---|---|\n| `a`, `b_c` | f |\n| `R1` | i |\n### `t2`\n| `z` | s |\n"
    assert v.documented_columns(text) == {"t1": {"a", "b_c", "R1"}, "t2": {"z"}}


def test_real_dictionary_documents_every_gold_column(tmp_path):
    for name in GOLD:
        shutil.copy(SAMPLE / f"gold_{name}.parquet", tmp_path / f"{name}.parquet")
    cov = v.dictionary_coverage(tmp_path)
    assert all(c["ok"] for c in cov), [c for c in cov if not c["ok"]]


def test_tokens_never_valued_detects_leak(tmp_path, monkeypatch):
    silver, gold = tmp_path / "silver" / "tables", tmp_path / "gold"
    silver.mkdir(parents=True)
    gold.mkdir()
    pd.DataFrame({"source_file": ["f", "f"], "source_row": [2, 3], "tad_k": [None, 2000.0],
                  "tad_k__flag": ["#DIV/0!", None]}).to_parquet(silver / "psi159__normal_flames.parquet")
    for s in ("psi159__inverse_flames", "psi10__normal_flames", "psi10__inverse_flames"):
        pd.DataFrame({"source_file": [], "source_row": []}).to_parquet(silver / f"{s}.parquet")
    pd.DataFrame({"source_file": ["f", "f"], "source_row": [2, 3], "tad_k": [0.0, 2000.0]}).to_parquet(gold / "gas_flame_tests.parquet")
    monkeypatch.setattr(v, "GOLD_FROM_SILVER", {"gas_flame_tests": v.GOLD_FROM_SILVER["gas_flame_tests"]})
    res = v.tokens_never_valued(silver, gold)
    assert res == [{"gold_table": "gas_flame_tests", "silver_table": "psi159__normal_flames", "column": "tad_k",
                    "flagged_rows": 1, "valued_in_gold": 1, "ok": False}]


@pytest.mark.integration
def test_full_g2_data_gate_passes():
    rep = v.run(write_summary=False)
    assert rep["passed"], rep["gate"]
