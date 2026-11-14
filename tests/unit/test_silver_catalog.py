"""DE-03 catalog flattening on a synthetic bronze snapshot (offline)."""

from __future__ import annotations

import hashlib
import json

import pandas as pd
import pytest

from flamesafe.pipeline import silver_catalog as sc

DETAIL_A = {
    "investigationAcronym": "FLEX",
    "title": "Flame Extinguishment Experiment ",
    "doi": "https://doi.org/10.60555/ABC",
    "researchArea": "Combustion Science",
    "projectType": "Microgravity Investigation",
    "investigationStartDate": "01-15-2008",
    "investigationEndDate": "not a date",
    "releaseDate": "24-Nov-2025",
    "licenseName": "",
    "related_glds": "PSI-68     PSI-100  PSI-68",
    "totalFileSize": 1.5e9,
    "added": [],
    "removed": [{"file_name": "old.csv", "file_size": 3, "remote_path": "/Home/psi-data/PSI-69/Raw Data/old.csv"}],
    "experimentalTable": [{"file_name": "PSI-69_Experimental table_FLEX.csv", "file_size": "24776",
                           "remote_path": "/Home/psi-data/PSI-69/Experimental table/PSI-69_Experimental table_FLEX.csv"}],
    "publications": [
        {"title": "Paper 1", "doi": "10.1016/J.X", "authorList": "A, B", "status": {"annotationValue": "published"}},
        {"title": "Paper 2", "doi": "", "authorList": "C", "status": {"annotationValue": "published"}},
    ],
    "contacts": [{"firstName": "Ada", "lastName": "L", "email": "ada@example.org", "phone": "123",
                  "fax": "", "address": "street", "affiliation": "Univ", "roles": [{"annotationValue": "PI"}]}],
}
DETAIL_B = {
    "investigationAcronym": "ACME",
    "projectType": "Ground Investigation",
    "licenseName": "Creative Commons Zero v1.0 Universal",
    "totalFileSize": "10",
    "added": [
        {"file_name": "a.csv", "file_size": 4.0, "remote_path": "/Home/psi-data/PSI-10/Experimental table/a.csv",
         "date_modified": {"$date": 1763671791274}, "restricted": False},
        {"file_name": "v.MP4", "file_size": 6, "remote_path": "/Home/psi-data/PSI-10/Raw Data/x/v.MP4"},
    ],
    "experimentalTable": [{"file_name": "a.csv", "file_size": 4}],
    "publications": [],
    "contacts": [],
}


@pytest.fixture
def snapshot(tmp_path):
    snap = tmp_path / "snapshot_2026-01-01"
    snap.mkdir()
    files = {}
    for psi_id, d in (("PSI-69", DETAIL_A), ("PSI-10", DETAIL_B)):
        raw = json.dumps(d).encode()
        (snap / f"{psi_id}.json").write_bytes(raw)
        files[f"{psi_id}.json"] = {"sha256": hashlib.sha256(raw).hexdigest(), "http_status": 200}
    search = {"hits": {"hits": [{"_source": {"Accession": "PSI-69", "Flight Platform": "ISS", "Keywords": "k"}}]}}
    (snap / "search.json").write_text(json.dumps(search))
    (snap / "manifest.json").write_text(json.dumps({"combustion_ids": ["PSI-10", "PSI-69"], "files": files}))
    return snap


def test_tables_reconcile_with_raw_and_have_provenance(snapshot):
    frames, report = sc.build_tables(snapshot)
    assert report["n_errors"] == 0
    assert all(v["ok"] for v in report["reconciliation"].values())
    assert report["row_counts"] == {"investigations": 2, "files": 3, "experimental_tables": 2,
                                    "publications": 2, "contacts": 1}
    for df in frames.values():
        assert {"snapshot", "source_file", "source_sha256"} <= set(df.columns)


def test_contacts_drop_pii(snapshot):
    frames, _ = sc.build_tables(snapshot)
    contacts = frames["contacts"]
    assert not set(sc.PII_CONTACT_FIELDS) & set(contacts.columns)
    assert "ada@example.org" not in contacts.to_csv()
    assert contacts.loc[0, "roles"] == "PI"


def test_investigation_fields_are_cleaned_not_imputed(snapshot):
    frames, report = sc.build_tables(snapshot)
    inv = frames["investigations"].set_index("psi_id")
    flex = inv.loc["PSI-69"]
    assert flex["title"] == "Flame Extinguishment Experiment"
    assert flex["doi"] == "10.60555/abc"
    assert flex["access_status"] == "experimental_table_only"
    assert flex["n_tables_not_in_added"] == 1 and flex["n_publications_with_doi"] == 1
    assert list(flex["related_investigations"]) == ["PSI-68", "PSI-100"]
    assert flex["start_date"] == pd.Timestamp("2008-01-15")
    assert pd.isna(flex["end_date"]) and pd.isna(flex["license_name"])
    assert flex["flight_platform"] == "ISS"
    assert inv.loc["PSI-10", "is_ground_investigation"]
    assert inv.loc["PSI-10", "registered_total_bytes"] == 10
    wheres = {i["where"] for i in report["issues"]}
    assert "PSI-69.investigationEndDate" in wheres and "PSI-69" in wheres  # bad date + empty license


def test_files_category_extension_and_table_flag(snapshot):
    frames, _ = sc.build_tables(snapshot)
    f = frames["files"].set_index("file_name")
    assert f.loc["a.csv", "category"] == "Experimental table" and f.loc["a.csv", "is_experimental_table"]
    assert f.loc["v.MP4", "category"] == "Raw Data" and f.loc["v.MP4", "extension"] == "mp4"
    assert f.loc["old.csv", "inventory"] == "removed"
    assert str(f.loc["a.csv", "date_modified"].tz) == "UTC"


def test_run_writes_parquet_and_report(snapshot, tmp_path):
    out = tmp_path / "silver"
    report = sc.run(snapshot, out)
    assert {p.name for p in out.glob("*.parquet")} == {f"{k}.parquet" for k in report["row_counts"]}
    assert (out / "_reports" / "catalog_parse_report.json").exists()
    assert len(pd.read_parquet(out / "files.parquet")) == 3


@pytest.mark.parametrize(("raw", "expected"), [
    ("10.1016/J.X", "10.1016/j.x"), ("https://dx.doi.org/10.1/A", "10.1/a"), ("doi: 10.2/b", "10.2/b"),
    ("", None), (None, None),
])
def test_normalize_doi(raw, expected):
    assert sc.normalize_doi(raw) == expected
