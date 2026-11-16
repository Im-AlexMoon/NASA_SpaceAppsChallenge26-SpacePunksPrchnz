"""DE-03 · Flatten the bronze catalog snapshot into silver tables (Parquet).

Outputs (data/silver/catalog/):
    investigations.parquet       one row per investigation (metadata + inventory counts + access status)
    files.parquet                one row per file in `added` (inventory='added') and `removed` (inventory='removed')
    experimental_tables.parquet  one row per curated experimental table (may be absent from `added`)
    publications.parquet         one row per publication attached to the PSI record
    contacts.parquet             investigators: name, affiliation, roles ONLY (no email/phone/fax/address)
    _reports/catalog_parse_report.json   row counts, reconciliation against the raw JSON, issues

Every row carries provenance: `snapshot`, `source_file`, `source_sha256`.
Nothing is imputed: empty strings become NULL, unparseable dates become NULL and are reported.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from flamesafe import config
from flamesafe.ingestion import catalog as bronze_catalog

PII_CONTACT_FIELDS = ("email", "phone", "fax", "address")
DOI_PREFIX = re.compile(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)
REPLACEMENT_CHAR = "�"


def silver_catalog_dir() -> Path:
    return config.data_dir() / "silver" / "catalog"


# ----------------------------------------------------------------------------- helpers
def _clean(value: Any) -> Any:
    """Strip strings; empty -> None. Leaves non-strings untouched."""
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _date(value: Any, fmt: str, issues: list, ctx: str) -> pd.Timestamp | None:
    value = _clean(value)
    if value is None:
        return None
    try:
        return pd.Timestamp(datetime.strptime(value, fmt))
    except ValueError:
        issues.append({"level": "warning", "where": ctx, "issue": f"unparseable date {value!r} (expected {fmt})"})
        return None


def _mongo_ts(value: Any) -> pd.Timestamp | None:
    if isinstance(value, dict) and "$date" in value:
        return pd.Timestamp(value["$date"], unit="ms", tz="UTC")
    return None


def _num(value: Any) -> float | None:
    try:
        return None if value in (None, "") else float(value)
    except (TypeError, ValueError):
        return None


def _category(remote_path: str | None, psi_id: str) -> str | None:
    """Folder right under /Home/psi-data/<PSI-ID>/ (e.g. 'Raw Data', 'Science Documents')."""
    if not remote_path:
        return None
    parts = remote_path.strip("/").split("/")
    try:
        i = parts.index(psi_id)
    except ValueError:
        return None
    return parts[i + 1] if len(parts) > i + 2 else None


def _ext(name: str | None) -> str | None:
    return name.rsplit(".", 1)[-1].lower() if name and "." in name else None


def normalize_doi(doi: Any) -> str | None:
    doi = _clean(doi)
    if doi is None:
        return None
    return DOI_PREFIX.sub("", doi).strip().lower() or None


def _related(value: Any) -> list[str]:
    return sorted(set(re.findall(r"PSI-\d+", value or "")), key=lambda s: int(s.split("-")[1]))


def _access_status(n_added: int, n_tables: int) -> str:
    if n_added > 0:
        return "available"
    return "experimental_table_only" if n_tables > 0 else "no_public_files"


# ----------------------------------------------------------------------------- builders
def build_tables(snapshot: Path) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    manifest = json.loads((snapshot / bronze_catalog.MANIFEST).read_text(encoding="utf-8"))
    search_by_id = {}
    for name in manifest.get("search_pages", ["search.json"]):
        search = json.loads((snapshot / name).read_text(encoding="utf-8"))
        for hit in search["hits"]["hits"]:
            source = hit.get("_source", {})
            if source.get("Accession"):
                search_by_id[source["Accession"]] = source
    issues: list[dict[str, str]] = []
    rows: dict[str, list[dict[str, Any]]] = {k: [] for k in
                                             ("investigations", "files", "experimental_tables", "publications", "contacts")}
    raw_counts = {"added": 0, "removed": 0, "experimental_tables": 0, "publications": 0, "contacts": 0}

    for psi_id in manifest["combustion_ids"]:
        source_file = f"{psi_id}.json"
        prov = {"snapshot": snapshot.name, "source_file": source_file,
                "source_sha256": manifest["files"][source_file]["sha256"]}
        d = json.loads((snapshot / source_file).read_text(encoding="utf-8"))
        s = search_by_id.get(psi_id, {})
        added, removed = d.get("added") or [], d.get("removed") or []
        tables, pubs, contacts = d.get("experimentalTable") or [], d.get("publications") or [], d.get("contacts") or []
        for k, v in (("added", added), ("removed", removed), ("experimental_tables", tables),
                     ("publications", pubs), ("contacts", contacts)):
            raw_counts[k] += len(v)
        added_names = {f.get("file_name") for f in added}
        table_names = {t.get("file_name") for t in tables}

        for field in ("objective", "approach", "hypothesis", "researchImpacts", "title"):
            if REPLACEMENT_CHAR in (d.get(field) or ""):
                issues.append({"level": "info", "where": f"{psi_id}.{field}", "issue": "contains U+FFFD"})

        rows["investigations"].append({
            "psi_id": psi_id,
            "acronym": _clean(d.get("investigationAcronym")),
            "title": _clean(d.get("title")),
            "doi": normalize_doi(d.get("doi")),
            "research_area": _clean(d.get("researchArea")),
            "sub_research_area": _clean(d.get("subResearchArea")),
            "project_type": _clean(d.get("projectType")),
            "is_ground_investigation": d.get("projectType") == "Ground Investigation",
            "flight_program": _clean(d.get("flightProgram")),
            "flight_platform": _clean(s.get("Flight Platform")),
            "experiment_hardware": _clean(d.get("experimentHardware")),
            "experiment_hardware_link": _clean(d.get("experimentHardwareLink")),
            "managing_center": _clean(d.get("managingNasaCenter")),
            "keywords": _clean(s.get("Keywords")),
            "related_investigations": _related(d.get("related_glds")),
            "start_date": _date(d.get("investigationStartDate"), "%m-%d-%Y", issues, f"{psi_id}.investigationStartDate"),
            "end_date": _date(d.get("investigationEndDate"), "%m-%d-%Y", issues, f"{psi_id}.investigationEndDate"),
            "release_date": _date(d.get("releaseDate"), "%d-%b-%Y", issues, f"{psi_id}.releaseDate"),
            "modified_date": _date(d.get("modifiedDate"), "%d-%b-%Y", issues, f"{psi_id}.modifiedDate"),
            "record_version": d.get("version"),
            "version_reason": _clean(d.get("versionReason")),
            "license_id": _clean(d.get("licenseIdentifier")),
            "license_name": _clean(d.get("licenseName")),
            "objective": _clean(d.get("objective")),
            "approach": _clean(d.get("approach")),
            "hypothesis": _clean(d.get("hypothesis")),
            "research_impacts": _clean(d.get("researchImpacts")),
            "description": _clean(d.get("description")),
            "n_added_files": len(added),
            "n_removed_files": len(removed),
            "n_experimental_tables": len(tables),
            "n_tables_not_in_added": len(table_names - added_names),
            "n_publications": len(pubs),
            "n_publications_with_doi": sum(normalize_doi(p.get("doi")) is not None for p in pubs),
            "added_bytes": int(sum(_num(f.get("file_size")) or 0 for f in added)),
            "registered_total_bytes": int(_num(d.get("totalFileSize")) or 0),
            "access_status": _access_status(len(added), len(tables)),
            **prov,
        })
        if not _clean(d.get("licenseName")):
            issues.append({"level": "info", "where": psi_id, "issue": "license field empty"})

        for inventory, files in (("added", added), ("removed", removed)):
            for f in files:
                name = _clean(f.get("file_name"))
                rows["files"].append({
                    "psi_id": psi_id,
                    "inventory": inventory,
                    "file_name": name,
                    "category": _category(f.get("remote_path"), psi_id),
                    "extension": _ext(name),
                    "file_bytes": _num(f.get("file_size")),
                    "file_version": f.get("version"),
                    "restricted": bool(f.get("restricted")),
                    "visible": f.get("visible"),
                    "is_experimental_table": name in table_names,
                    "date_created": _mongo_ts(f.get("date_created")),
                    "date_modified": _mongo_ts(f.get("date_modified")),
                    "remote_path": _clean(f.get("remote_path")),
                    **prov,
                })

        for t in tables:
            name = _clean(t.get("file_name"))
            rows["experimental_tables"].append({
                "psi_id": psi_id,
                "file_name": name,
                "extension": _ext(name),
                "listed_bytes": _num(t.get("file_size")),
                "in_added": name in added_names,
                "restricted": bool(t.get("restricted")),
                "subcategory": _clean(t.get("subcategory")),
                "date_modified": _mongo_ts(t.get("date_modified")),
                "remote_path": _clean(t.get("remote_path")),
                **prov,
            })

        for i, p in enumerate(pubs):
            status = p.get("status")
            rows["publications"].append({
                "psi_id": psi_id,
                "pub_index": i,
                "title": _clean(p.get("title")),
                "doi": normalize_doi(p.get("doi")),
                "author_list": _clean(p.get("authorList")),
                "status": _clean(status.get("annotationValue")) if isinstance(status, dict) else _clean(status),
                "pubmed_id": _clean(p.get("pubMedID")),
                **prov,
            })

        for c in contacts:
            rows["contacts"].append({
                "psi_id": psi_id,
                "first_name": _clean(c.get("firstName")),
                "mid_initials": _clean(c.get("midInitials")),
                "last_name": _clean(c.get("lastName")),
                "affiliation": _clean(c.get("affiliation")),
                "roles": "; ".join(r.get("annotationValue", "") for r in c.get("roles") or [] if r.get("annotationValue")) or None,
                **prov,
            })

    frames = {k: pd.DataFrame(v) for k, v in rows.items()}
    report = _report(snapshot, frames, raw_counts, issues)
    return frames, report


def _report(snapshot: Path, frames: dict[str, pd.DataFrame], raw: dict[str, int], issues: list) -> dict[str, Any]:
    files = frames["files"]
    n_added = int((files["inventory"] == "added").sum()) if len(files) else 0
    n_removed = int((files["inventory"] == "removed").sum()) if len(files) else 0
    recon = {
        "added_files": {"raw": raw["added"], "silver": n_added},
        "removed_files": {"raw": raw["removed"], "silver": n_removed},
        "experimental_tables": {"raw": raw["experimental_tables"], "silver": len(frames["experimental_tables"])},
        "publications": {"raw": raw["publications"], "silver": len(frames["publications"])},
        "contacts": {"raw": raw["contacts"], "silver": len(frames["contacts"])},
    }
    for k, v in recon.items():
        v["ok"] = v["raw"] == v["silver"]
        if not v["ok"]:
            issues.append({"level": "error", "where": k, "issue": f"row count mismatch {v}"})
    pii_leak = [c for c in PII_CONTACT_FIELDS if c in frames["contacts"].columns]
    if pii_leak:
        issues.append({"level": "error", "where": "contacts", "issue": f"PII columns present: {pii_leak}"})
    return {
        "built_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "snapshot": snapshot.name,
        "row_counts": {k: len(v) for k, v in frames.items()},
        "reconciliation": recon,
        "issues": issues,
        "n_errors": sum(i["level"] == "error" for i in issues),
    }


def run(snapshot: Path | None = None, out_dir: Path | None = None) -> dict[str, Any]:
    snapshot = snapshot or bronze_catalog.latest_snapshot()
    out_dir = out_dir or silver_catalog_dir()
    frames, report = build_tables(snapshot)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in frames.items():
        df.to_parquet(out_dir / f"{name}.parquet", index=False)
    (out_dir / "_reports").mkdir(exist_ok=True)
    with open(out_dir / "_reports" / "catalog_parse_report.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, default=str)
        fh.write("\n")
    report["out_dir"] = str(out_dir)
    return report
