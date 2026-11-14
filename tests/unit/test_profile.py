"""DE-04: tabular profiler, profile docs preservation, selection-driven downloader (offline)."""

from __future__ import annotations

import json

import pandas as pd
import pytest
from fakes import FakeResponse, make_client

from flamesafe.ingestion import download as dl
from flamesafe.ingestion import profile_docs
from flamesafe.ingestion.profile import parse_unit, profile_csv, profile_file


# ----------------------------------------------------------------------------- profiler
def test_csv_with_tokens_trailing_blanks_and_units(tmp_path):
    p = tmp_path / "t.csv"
    p.write_text("Test,XO2,Tad (K),Burning rate; mm\nA1,0.21,2000,0.5\nA2,RAMP,#DIV/0!,0.6\nA3,0.4,2100,\n,,,\n,,,\n",
                 encoding="utf-8")
    prof = profile_csv(p)
    assert prof["physical_rows"] == 5 and prof["nonempty_rows"] == 3 and prof["n_columns"] == 4
    cols = {c["name"]: c for c in prof["columns"]}
    assert cols["XO2"]["kind"] == "mixed" and cols["XO2"]["non_numeric_tokens"] == {"RAMP": 1}
    assert cols["Tad (K)"]["unit_in_header"] == "K" and cols["Tad (K)"]["min"] == 2000
    assert cols["Burning rate; mm"]["unit_in_header"] == "mm" and cols["Burning rate; mm"]["non_empty"] == 2


def test_csv_metadata_preamble_and_bom(tmp_path):
    p = tmp_path / "raw.csv"
    p.write_bytes("﻿2019-07-15 196 ,Experiment: 0,Test Point: 19196B1,MFCA1 Gas: 2\nTime,Flow,PMT\n"
                  "18:03:27,0.1,1.8\n18:03:28,0.2,1.9\n".encode())
    prof = profile_csv(p)
    assert prof["encoding"] == "utf-8-bom"
    assert prof["metadata_preamble"]["Test Point"] == "19196B1"
    assert prof["header_row"] == 2 and prof["nonempty_rows"] == 2
    assert [c["name"] for c in prof["columns"]] == ["Time", "Flow", "PMT"]


def test_cp1252_fallback_and_side_by_side_blocks(tmp_path):
    p = tmp_path / "b.csv"
    p.write_bytes("P (atm),Dext,,P (atm),Dmodel\n0.5,3.48,,0.5,3.43\n1,\x96,,1,3.1\n".encode("latin-1"))
    prof = profile_csv(p)
    assert prof["encoding"] == "cp1252" and prof["n_blocks"] == 2
    assert prof["columns"][1]["non_numeric_tokens"] == {"–": 1}


def test_xlsx_header_detection_skips_title_rows(tmp_path):
    p = tmp_path / "w.xlsx"
    with pd.ExcelWriter(p) as xw:
        pd.DataFrame([["BASS Test Matrix", None, None], [None, None, None], ["Test", "O2 % by volume", "pressure, atm"],
                      [1, 21.0, 1.0], [2, 18.5, 1.0]]).to_excel(xw, sheet_name="m", header=False, index=False)
    prof = profile_file(p)
    sh = prof["sheets"][0]
    assert prof["format"] == "xlsx" and sh["header_row"] == 3 and sh["nonempty_rows"] == 2
    assert sh["columns"][1]["kind"] == "numeric" and sh["columns"][1]["max"] == 21.0


def test_non_tabular_is_reported_not_raised(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(b"%PDF")
    assert profile_file(p)["profiled"] is False


@pytest.mark.parametrize(("h", "u"), [("mfuel (mg/s)", "mg/s"), ("Ambient pressure; mmHg", "mmHg"), ("Fuel", None)])
def test_parse_unit(h, u):
    assert parse_unit(h) == u


# ----------------------------------------------------------------------------- docs
def test_profile_regeneration_preserves_manual_block(tmp_path):
    path = tmp_path / "PSI-1.md"
    auto1 = f"{profile_docs.AUTO_BEGIN}\nold facts\n{profile_docs.AUTO_END}"
    assert profile_docs.write_profile(path, "# PSI-1 — A", auto1) == "created"
    text = path.read_text(encoding="utf-8").replace("_por completar_", "Mi evaluación", 1)
    path.write_text(text, encoding="utf-8")
    auto2 = f"{profile_docs.AUTO_BEGIN}\nnew facts\n{profile_docs.AUTO_END}"
    assert profile_docs.write_profile(path, "# PSI-1 — A v2", auto2) == "updated"
    out = path.read_text(encoding="utf-8")
    assert "new facts" in out and "old facts" not in out and "Mi evaluación" in out
    assert out.startswith("# PSI-1 — A v2\n")


# ----------------------------------------------------------------------------- downloader
@pytest.fixture
def silver(tmp_path):
    d = tmp_path / "silver"
    d.mkdir()
    pd.DataFrame([{"psi_id": "PSI-1", "inventory": "added", "file_name": "a.csv", "file_bytes": 4.0},
                  {"psi_id": "PSI-1", "inventory": "removed", "file_name": "old.csv", "file_bytes": 1.0}]
                 ).to_parquet(d / "files.parquet")
    pd.DataFrame([{"psi_id": "PSI-1", "file_name": "et.csv", "listed_bytes": 3.0}]).to_parquet(d / "experimental_tables.parquet")
    return d


def test_requests_resolve_and_reject_unknown_or_removed(silver):
    reqs = dl.requests_from_l2({"include_experimental_tables": True, "samples": {"PSI-1": ["a.csv"]}}, silver)
    assert [(r.file_name, r.list_source) for r in reqs] == [("a.csv", "added"), ("et.csv", "experimentalTable")]
    with pytest.raises(KeyError):
        dl.requests_from_l2({"samples": {"PSI-1": ["old.csv"]}}, silver)  # removed != current inventory


def test_budget_guardrails():
    reqs = [dl.FileRequest("PSI-1", "v.mp4", 10, "added"), dl.FileRequest("PSI-1", "big.csv", int(40e6), "added")]
    with pytest.raises(dl.BudgetError) as exc:
        dl.check_budget(reqs, max_total_mb=30, max_file_mb=30, deny_extensions=["mp4"])
    msg = str(exc.value)
    assert ".mp4 denied" in msg and "> 30 MB" in msg and "total" in msg


def test_fetch_writes_sidecar_reuses_and_records_404(tmp_path):
    reqs = [dl.FileRequest("PSI-1", "a.csv", 4, "added"), dl.FileRequest("PSI-1", "gone.csv", 9, "added")]
    client, _ = make_client({"file=a.csv": [FakeResponse(body=b"x,y\n")], "file=gone.csv": [FakeResponse(404)]})
    res = dl.fetch(reqs, client=client, root=tmp_path)
    assert [r["action"] for r in res] == ["fetched", "http_404"]
    meta = json.loads((tmp_path / "PSI-1" / "a.csv.meta.json").read_text())
    assert meta["size_matches"] and meta["sha256"] and "REDACTED" not in meta["source_url"]
    assert not (tmp_path / "PSI-1" / "gone.csv").exists()
    assert json.loads((tmp_path / "PSI-1" / "gone.csv.meta.json").read_text())["http_status"] == 404
    client2, session2 = make_client({})
    assert dl.fetch(reqs[:1], client=client2, root=tmp_path)[0]["action"] == "reused" and session2.calls == []
