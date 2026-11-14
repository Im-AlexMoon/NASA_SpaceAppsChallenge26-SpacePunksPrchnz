"""PSI client + verification logic, fully offline (fake HTTP session)."""

from __future__ import annotations

import hashlib

import pytest
from fakes import SETTINGS, FakeResponse, make_client

from flamesafe.ingestion import verify
from flamesafe.ingestion.psi_client import PSIError, redact_url

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


def test_url_quotes_file_names_with_spaces():
    client, _ = make_client({})
    url = client.url("download", psi_id="PSI-69", filename="PSI-69_Experimental table_FLEX.csv")
    assert url == "https://psi.example/ws/studies/PSI-69/download?file=PSI-69_Experimental%20table_FLEX.csv"


def test_redact_url_removes_temporary_credentials():
    url = "https://b.s3.amazonaws.com/f.csv?versionId=v1&AWSAccessKeyId=ASIAXXX&Signature=abc%3D&x-amz-security-token=TOKEN"
    out = redact_url(url)
    assert "ASIAXXX" not in out and "abc" not in out and "TOKEN" not in out
    assert "versionId=v1" in out


def test_list_investigations_filters_and_sorts_numerically():
    client, _ = make_client({"/repo/search": [FakeResponse(body=SEARCH)]})
    ids = [s["Accession"] for s in client.list_investigations("Combustion Science")]
    assert ids == ["PSI-10", "PSI-100"]


def test_404_is_not_retried():
    client, session = make_client({"/download": [FakeResponse(404)]})
    assert client.probe("PSI-1", "missing.csv") == 404
    assert len(session.calls) == 1


def test_503_is_retried_then_succeeds():
    client, session = make_client({"/repo/investigations/": [FakeResponse(503), FakeResponse(body={"ok": 1})]})
    assert client.investigation("PSI-10") == {"ok": 1}
    assert len(session.calls) == 2


def test_persistent_503_raises_after_retries():
    client, session = make_client({"/repo/investigations/": [FakeResponse(503)]})
    with pytest.raises(PSIError) as exc:
        client.investigation("PSI-10")
    assert exc.value.status == 503 and len(session.calls) == SETTINGS["request"]["retries"]


def test_download_hashes_and_writes_atomically(tmp_path):
    payload = b"a,b\n1,2\n" * 1000
    client, _ = make_client({"/download": [FakeResponse(body=payload, headers={"Content-Type": "text/csv"})]})
    dest = tmp_path / "PSI-1" / "t.csv"
    res = client.download("PSI-1", "t.csv", dest, chunk=64)
    assert dest.read_bytes() == payload
    assert res.sha256 == hashlib.sha256(payload).hexdigest() and res.bytes == len(payload)
    assert not dest.with_suffix(".csv.part").exists()


@pytest.mark.parametrize(
    ("n_added", "n_tables", "expected"),
    [(5, 0, "available"), (0, 1, "experimental_table_only"), (0, 0, "no_public_files")],
)
def test_access_status(n_added, n_tables, expected):
    assert verify.access_status(n_added, n_tables) == expected


def test_summarize_detail_counts_tables_outside_added():
    detail = {
        "doi": "10.x/y",
        "added": [{"file_name": "a.csv", "file_size": 10.0}, {"file_name": "v.mp4", "file_size": 90, "restricted": True}],
        "experimentalTable": [{"file_name": "a.csv", "file_size": 10}, {"file_name": "et.csv", "file_size": "5"}],
        "removed": [{}],
        "publications": [{}, {}],
        "totalFileSize": 1e12,
    }
    s = verify.summarize_detail(detail)
    assert s["n_added"] == 2 and s["n_experimental_tables"] == 2
    assert s["n_tables_not_in_added"] == 1 and s["n_restricted_added"] == 1
    assert s["added_bytes"] == 100 and s["registered_total_bytes"] == 10**12
    assert s["extensions"] == {"csv": 1, "mp4": 1}
    assert s["access_status"] == "available"
