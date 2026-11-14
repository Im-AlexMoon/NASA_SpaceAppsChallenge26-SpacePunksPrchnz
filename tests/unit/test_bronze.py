"""DE-06: manifest lock round-trip, drift detection, integrity verification, duplicates (offline)."""

from __future__ import annotations

import json

import pandas as pd
from fakes import FakeResponse, make_client

from flamesafe import config
from flamesafe.ingestion import download as dl


def _silver(tmp_path, added_bytes=4.0):
    d = tmp_path / "silver"
    d.mkdir()
    pd.DataFrame([{"psi_id": "PSI-1", "inventory": "added", "file_name": "a.csv", "file_bytes": added_bytes}]
                 ).to_parquet(d / "files.parquet")
    pd.DataFrame([{"psi_id": "PSI-1", "file_name": "et.csv", "listed_bytes": 3.0}]).to_parquet(d / "experimental_tables.parquet")
    return d


def test_lock_roundtrip(tmp_path):
    reqs = [dl.FileRequest("PSI-1", "a.csv", 4, "added", "g1"), dl.FileRequest("PSI-1", "et.csv", 3, "experimentalTable", "experimental_table")]
    lock = dl.write_manifest_lock(reqs, tmp_path / "lock.csv")
    assert dl.requests_from_lock(lock) == reqs


def test_lock_drift_flags_resized_and_delisted(tmp_path):
    silver = _silver(tmp_path, added_bytes=5.0)
    reqs = [dl.FileRequest("PSI-1", "a.csv", 4, "added", "g"), dl.FileRequest("PSI-1", "et.csv", 3, "experimentalTable", "g"),
            dl.FileRequest("PSI-1", "gone.csv", 1, "added", "g")]
    drift = dl.lock_drift(reqs, silver)
    assert any("a.csv: listed bytes 5 != lock 4" in d for d in drift)
    assert any("gone.csv: no longer listed" in d for d in drift)
    assert not any("et.csv" in d for d in drift)


def test_verify_integrity_detects_corruption_orphans_and_partials(tmp_path):
    client, _ = make_client({"file=a.csv": [FakeResponse(body=b"1234")]})
    dl.fetch([dl.FileRequest("PSI-1", "a.csv", 4, "added", "g")], client=client, root=tmp_path)
    assert dl.verify_integrity(tmp_path) == {"files_checked": 1, "problems": [], "orphans": [], "partials": []}
    (tmp_path / "PSI-1" / "a.csv").write_bytes(b"XXXX")
    (tmp_path / "PSI-1" / "stray.csv").write_bytes(b"x")
    (tmp_path / "PSI-1" / "b.csv.part").write_bytes(b"x")
    integ = dl.verify_integrity(tmp_path)
    assert integ["problems"] == ["sha256 mismatch: PSI-1/a.csv"]
    assert "PSI-1/stray.csv" in integ["orphans"] and integ["partials"] == ["PSI-1/b.csv.part"]


def test_reused_file_takes_current_group_and_checks_size(tmp_path):
    client, _ = make_client({"file=a.csv": [FakeResponse(body=b"1234")]})
    dl.fetch([dl.FileRequest("PSI-1", "a.csv", 4, "added", "L2 sample")], client=client, root=tmp_path)
    client2, _ = make_client({})
    res = dl.fetch([dl.FileRequest("PSI-1", "a.csv", 5, "added", "mvp_rq2")], client=client2, root=tmp_path)[0]
    assert res["reason"] == "mvp_rq2" and res["action"] == "reused_size_mismatch" and res["size_matches"] is False


def test_report_groups_and_duplicates(tmp_path):
    results = [
        {"psi_id": "PSI-1", "file_name": "a.csv", "reason": "g1", "bytes": 4, "sha256": "s1", "http_status": 200, "action": "fetched"},
        {"psi_id": "PSI-2", "file_name": "b.csv", "reason": "g1", "bytes": 4, "sha256": "s1", "http_status": 200, "action": "reused"},
        {"psi_id": "PSI-2", "file_name": "c.csv", "reason": "g2", "bytes": 0, "http_status": 404, "action": "http_404"},
    ]
    path = dl.write_report(results, "t", root=tmp_path / "files", extra={"lock": "x.csv"})
    rep = json.loads(path.read_text())
    assert rep["duplicate_content_groups"] == [["PSI-1/a.csv", "PSI-2/b.csv"]]
    assert rep["by_group"]["g1"] == {"n": 2, "bytes": 8} and rep["n_ok"] == 2 and rep["lock"] == "x.csv"


def test_committed_lock_matches_manifest_budget():
    lock = config.ROOT / "docs" / "02_data_engineering" / "acquisition_manifest.csv"
    reqs = dl.requests_from_lock(lock)
    b = config.load("acquisition_manifest")["budget"]
    dl.check_budget(reqs, b["max_total_mb"], b["max_file_mb"],
                    config.load("sources")["download_budget"]["deny_extensions"], b["max_files"])
    assert len({(r.psi_id, r.file_name) for r in reqs}) == len(reqs)  # no duplicates in the lock
