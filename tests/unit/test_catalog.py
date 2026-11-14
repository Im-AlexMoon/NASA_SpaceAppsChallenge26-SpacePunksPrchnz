"""DE-02 catalog snapshot, offline."""

from __future__ import annotations

import hashlib
import json

from fakes import FakeResponse, make_client

from flamesafe.ingestion import catalog

SEARCH = {
    "hits": {
        "total": 3,
        "hits": [
            {"_source": {"Accession": "PSI-100", "Research Area": "Combustion Science"}},
            {"_source": {"Accession": "PSI-7", "Research Area": "Fluid Physics"}},
            {"_source": {"Accession": "PSI-10", "Research Area": "Combustion Science"}},
        ],
    }
}


def routes(detail_100=None):
    return {
        "/repo/search": [FakeResponse(body=SEARCH)],
        "/repo/investigations/PSI-10": [FakeResponse(body={"accession": "PSI-10", "added": []})],
        "/repo/investigations/PSI-100": [detail_100 or FakeResponse(body={"accession": "PSI-100"})],
    }


def test_snapshot_writes_raw_files_manifest_and_latest(tmp_path):
    client, _ = make_client(routes())
    res = catalog.run(client, root=tmp_path, snapshot_name="snapshot_2026-01-01")
    snap = tmp_path / "snapshot_2026-01-01"

    assert res.complete and res.combustion_ids == ["PSI-10", "PSI-100"]
    assert sorted(p.name for p in snap.iterdir()) == ["PSI-10.json", "PSI-100.json", "manifest.json", "search.json"]
    manifest = json.loads((snap / "manifest.json").read_text())
    raw = (snap / "PSI-10.json").read_bytes()
    assert manifest["files"]["PSI-10.json"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert manifest["complete"] is True
    assert catalog.latest_snapshot(tmp_path) == snap
    assert set(catalog.load_details(snap)) == {"PSI-10", "PSI-100"}


def test_rerun_same_day_reuses_valid_files(tmp_path):
    client, _ = make_client(routes())
    catalog.run(client, root=tmp_path, snapshot_name="snapshot_x")
    client2, session2 = make_client(routes())
    res = catalog.run(client2, root=tmp_path, snapshot_name="snapshot_x")
    assert res.fetched == [] and len(res.reused) == 3
    assert session2.calls == []


def test_corrupted_cached_file_is_refetched(tmp_path):
    client, _ = make_client(routes())
    catalog.run(client, root=tmp_path, snapshot_name="snapshot_x")
    (tmp_path / "snapshot_x" / "PSI-10.json").write_text("tampered")
    client2, _ = make_client(routes())
    res = catalog.run(client2, root=tmp_path, snapshot_name="snapshot_x")
    assert res.fetched == ["PSI-10.json"]


def test_failed_record_marks_snapshot_incomplete_and_keeps_latest(tmp_path):
    client, _ = make_client(routes())
    catalog.run(client, root=tmp_path, snapshot_name="snapshot_a")
    client2, _ = make_client(routes(detail_100=FakeResponse(503)))
    res = catalog.run(client2, root=tmp_path, snapshot_name="snapshot_b")
    assert res.failed == {"PSI-100": 503} and not res.complete
    assert catalog.latest_snapshot(tmp_path).name == "snapshot_a"


def test_drift_detects_changed_records(tmp_path):
    client, _ = make_client(routes())
    catalog.run(client, root=tmp_path, snapshot_name="snapshot_a")
    client2, _ = make_client(routes(detail_100=FakeResponse(body={"accession": "PSI-100", "added": [1]})))
    res = catalog.run(client2, root=tmp_path, snapshot_name="snapshot_b")
    assert res.drift["changed"] == ["PSI-100.json"]
    assert res.drift["compared_with"] == ["snapshot_a"]
