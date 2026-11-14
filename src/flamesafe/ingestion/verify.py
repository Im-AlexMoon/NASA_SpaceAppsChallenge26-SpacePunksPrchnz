"""DE-01 · Reproducible verification of the PSI API.

Hits the three endpoints, summarizes the combustion collection and re-checks known access issues,
then writes a JSON report (metadata only: no data files, no credentials) that is committed as evidence
under docs/02_data_engineering/verification/.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from flamesafe import config
from flamesafe.ingestion.psi_client import PSIClient, PSIError

# Claims from the reference repo (snapshot 2026-11-08) that we re-check — see ADR-0003.
KNOWN_ISSUES: list[dict[str, str]] = [
    {"psi_id": "PSI-98", "file_name": "PSI-98_Raw Data_Saffire-I Telemetry Data Good Process Version.xlsx",
     "claim": "listed but HTTP 404"},
    {"psi_id": "PSI-98", "file_name": "PSI-98_Raw Data_Saffire-I Sample 1 Sensor Data Complete TM graphs.xlsx",
     "claim": "listed but HTTP 404"},
    {"psi_id": "PSI-98", "file_name": "PSI-98_Raw Data_Saffire-I Sample 2 Sensor Data Complete TM graphs.xlsx",
     "claim": "not stated (sibling of the files above)"},
]


def access_status(n_added: int, n_tables: int) -> str:
    if n_added > 0:
        return "available"
    if n_tables > 0:
        return "experimental_table_only"
    return "no_public_files"


def summarize_detail(detail: dict[str, Any]) -> dict[str, Any]:
    added = detail.get("added") or []
    tables = detail.get("experimentalTable") or []
    added_names = {f.get("file_name") for f in added}
    return {
        "doi": detail.get("doi"),
        "acronym": detail.get("investigationAcronym"),
        "version": detail.get("version"),
        "modified_date": detail.get("modifiedDate"),
        "n_added": len(added),
        "n_removed": len(detail.get("removed") or []),
        "n_experimental_tables": len(tables),
        "n_tables_not_in_added": sum(t.get("file_name") not in added_names for t in tables),
        "n_restricted_added": sum(bool(f.get("restricted")) for f in added),
        "n_publications": len(detail.get("publications") or []),
        "added_bytes": int(sum(float(f.get("file_size") or 0) for f in added)),
        "registered_total_bytes": int(float(detail.get("totalFileSize") or 0)),
        "license_name": detail.get("licenseName") or None,
        "access_status": access_status(len(added), len(tables)),
        "experimental_tables": [
            {"file_name": t.get("file_name"), "listed_bytes": int(float(t.get("file_size") or 0)),
             "in_added": t.get("file_name") in added_names, "restricted": bool(t.get("restricted"))}
            for t in tables
        ],
        "extensions": dict(Counter(_ext(f.get("file_name", "")) for f in added).most_common()),
    }


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def run(client: PSIClient | None = None, *, download_tables: bool = True) -> dict[str, Any]:
    client = client or PSIClient()
    area = config.load("sources")["psi"]["research_area_filter"]
    expected = config.load("sources")["psi"].get("expected_combustion_investigations")
    t0 = time.monotonic()
    report: dict[str, Any] = {
        "verified_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "base_url": client.base_url,
        "endpoints": {},
    }

    # 1 · search ---------------------------------------------------------------------------
    search = client.search()
    sources = list(client.iter_sources(search))
    combustion = sorted((s for s in sources if s.get("Research Area") == area),
                        key=lambda s: int(s["Accession"].split("-")[1]))
    report["endpoints"]["search"] = {"http_status": 200, "url": client.url("search")}
    report["collection"] = {
        "total_investigations": len(sources),
        "reported_total": search.get("hits", {}).get("total"),
        "by_research_area": dict(Counter(s.get("Research Area") for s in sources).most_common()),
        "combustion_count": len(combustion),
        "combustion_count_matches_expected": len(combustion) == expected,
    }

    # 2 · detail for every combustion record -----------------------------------------------
    investigations: list[dict[str, Any]] = []
    for s in combustion:
        psi_id = s["Accession"]
        row: dict[str, Any] = {
            "psi_id": psi_id,
            "acronym_search": s.get("Acronym") or None,
            "title": s.get("Title"),
            "sub_research_area": s.get("SubResearch Area") or None,
            "project_type": s.get("Project Type"),
            "flight_platform": s.get("Flight Platform") or None,
            "experiment_hardware": s.get("Experiment Hardware") or None,
        }
        try:
            row.update(summarize_detail(client.investigation(psi_id)))
            row["detail_http_status"] = 200
        except PSIError as exc:
            row["detail_http_status"] = exc.status
        investigations.append(row)
    report["endpoints"]["investigation"] = {
        "http_200": sum(r["detail_http_status"] == 200 for r in investigations),
        "requested": len(investigations),
    }
    report["investigations"] = investigations

    # 3 · download endpoint on every experimental table ------------------------------------
    table_checks: list[dict[str, Any]] = []
    if download_tables:
        with tempfile.TemporaryDirectory() as tmp:
            for inv in investigations:
                for t in inv.get("experimental_tables", []):
                    check = {"psi_id": inv["psi_id"], "file_name": t["file_name"],
                             "listed_bytes": t["listed_bytes"]}
                    try:
                        res = client.download(inv["psi_id"], t["file_name"], Path(tmp) / "f")
                        check.update(http_status=200, bytes=res.bytes, sha256=res.sha256,
                                     size_matches_listing=res.bytes == t["listed_bytes"])
                    except PSIError as exc:
                        check.update(http_status=exc.status)
                    table_checks.append(check)
    report["experimental_table_downloads"] = table_checks
    report["endpoints"]["download"] = {
        "tables_http_200": sum(c.get("http_status") == 200 for c in table_checks),
        "tables_requested": len(table_checks),
        "tables_size_match": sum(bool(c.get("size_matches_listing")) for c in table_checks),
    }

    # 4 · re-check claims from the reference repo + negative controls ----------------------
    report["known_issue_rechecks"] = [
        {**k, "http_status_now": client.probe(k["psi_id"], k["file_name"])} for k in KNOWN_ISSUES
    ]
    report["negative_controls"] = {
        "unknown_file_http_status": client.probe("PSI-69", "__flamesafe_nonexistent__.csv"),
        "unknown_investigation_http_status": _detail_status(client, "PSI-999999"),
    }

    # 5 · totals ---------------------------------------------------------------------------
    ok = [r for r in investigations if r["detail_http_status"] == 200]
    report["totals"] = {
        "added_files": sum(r["n_added"] for r in ok),
        "experimental_tables": sum(r["n_experimental_tables"] for r in ok),
        "experimental_tables_not_in_added": sum(r["n_tables_not_in_added"] for r in ok),
        "experimental_table_bytes": sum(c.get("bytes", 0) for c in table_checks),
        "registered_total_bytes": sum(r["registered_total_bytes"] for r in ok),
        "access_status": dict(Counter(r["access_status"] for r in ok)),
        "ground_investigations": [r["psi_id"] for r in investigations
                                  if r["project_type"] == "Ground Investigation"],
    }
    report["elapsed_s"] = round(time.monotonic() - t0, 1)
    report["report_sha256"] = hashlib.sha256(
        json.dumps({k: v for k, v in report.items() if k != "elapsed_s"}, sort_keys=True).encode()
    ).hexdigest()
    return report


def _detail_status(client: PSIClient, psi_id: str) -> int:
    try:
        client.investigation(psi_id)
        return 200
    except PSIError as exc:
        return exc.status


def default_output() -> Path:
    day = datetime.now(UTC).date().isoformat()
    return config.ROOT / "docs" / "02_data_engineering" / "verification" / f"api_verification_{day}.json"


def write(report: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
