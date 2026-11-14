"""DE-02 · Snapshot the PSI combustion catalog into bronze (metadata only, no data files).

Layout (one immutable snapshot per UTC day; re-running the same day resumes):

    data/bronze/catalog/
        LATEST                          # name of the most recent complete snapshot
        snapshot_YYYY-MM-DD/
            search.json                 # raw search response (all research areas)
            PSI-XX.json                 # raw detail response per combustion investigation, verbatim
            manifest.json               # per file: url, retrieved_at_utc, http_status, bytes, sha256

Raw responses are stored byte-for-byte as served. They contain PI contact details (names, emails):
bronze is git-ignored and silver must drop those fields (DE-03).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from flamesafe import config
from flamesafe.ingestion.psi_client import PSIClient, PSIError

MANIFEST = "manifest.json"
LATEST = "LATEST"


@dataclass
class CatalogResult:
    snapshot_dir: Path
    fetched: list[str] = field(default_factory=list)
    reused: list[str] = field(default_factory=list)
    failed: dict[str, int] = field(default_factory=dict)
    combustion_ids: list[str] = field(default_factory=list)
    drift: dict[str, list[str]] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        return not self.failed


def catalog_root() -> Path:
    return config.data_dir() / "bronze" / "catalog"


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def _load_manifest(snapshot: Path) -> dict[str, Any]:
    path = snapshot / MANIFEST
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"files": {}}


def _store(snapshot: Path, manifest: dict, name: str, url: str, raw: bytes) -> None:
    (snapshot / name).write_bytes(raw)
    manifest["files"][name] = {
        "url": url,
        "retrieved_at_utc": _now(),
        "http_status": 200,
        "bytes": len(raw),
        "sha256": _sha256(raw),
    }


def _valid_cached(snapshot: Path, manifest: dict, name: str) -> bool:
    entry = manifest["files"].get(name)
    path = snapshot / name
    return bool(entry and entry.get("http_status") == 200 and path.exists()
                and _sha256(path.read_bytes()) == entry["sha256"])


def previous_snapshot(root: Path, current: Path) -> Path | None:
    older = sorted(p for p in root.glob("snapshot_*") if p.is_dir() and p.name < current.name)
    return older[-1] if older else None


def drift_against(previous: Path | None, manifest: dict) -> dict[str, list[str]]:
    """Compare per-file sha256 with the previous snapshot (detects metadata/inventory changes)."""
    if previous is None:
        return {}
    def ok(files: dict) -> dict:  # only successfully retrieved files carry a sha256
        return {n: e for n, e in files.items() if "sha256" in e}

    old = ok(_load_manifest(previous)["files"])
    new = ok(manifest["files"])
    return {
        "changed": sorted(n for n in new if n in old and old[n]["sha256"] != new[n]["sha256"]),
        "added": sorted(n for n in new if n not in old),
        "missing": sorted(n for n in old if n not in new),
        "compared_with": [previous.name],
    }


def run(
    client: PSIClient | None = None,
    *,
    root: Path | None = None,
    snapshot_name: str | None = None,
    refresh: bool = False,
    progress: Callable[[str, str], None] | None = None,
) -> CatalogResult:
    client = client or PSIClient()
    root = root or catalog_root()
    snapshot = root / (snapshot_name or f"snapshot_{datetime.now(UTC).date().isoformat()}")
    snapshot.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest(snapshot)
    area = config.load("sources")["psi"]["research_area_filter"]
    result = CatalogResult(snapshot)
    say = progress or (lambda *_: None)

    # 1 · search (always first: defines which records belong to the snapshot)
    search_url = client.url("search")
    if not refresh and _valid_cached(snapshot, manifest, "search.json"):
        result.reused.append("search.json")
    else:
        _store(snapshot, manifest, "search.json", search_url, client.get_raw(search_url))
        result.fetched.append("search.json")
    search = json.loads((snapshot / "search.json").read_text(encoding="utf-8"))
    combustion = sorted(
        (s["Accession"] for s in client.iter_sources(search) if s.get("Research Area") == area),
        key=lambda a: int(a.split("-")[1]),
    )
    result.combustion_ids = combustion

    # 2 · detail per combustion record
    for psi_id in combustion:
        name = f"{psi_id}.json"
        if not refresh and _valid_cached(snapshot, manifest, name):
            result.reused.append(name)
            say(psi_id, "cached")
            continue
        url = client.url("investigation", psi_id=psi_id)
        try:
            _store(snapshot, manifest, name, url, client.get_raw(url))
            result.fetched.append(name)
            say(psi_id, "fetched")
        except PSIError as exc:
            manifest["files"][name] = {"url": url, "retrieved_at_utc": _now(), "http_status": exc.status}
            result.failed[psi_id] = exc.status
            say(psi_id, f"HTTP {exc.status}")
        _write_json(snapshot / MANIFEST, manifest)  # checkpoint after every record

    manifest.update(
        snapshot=snapshot.name,
        research_area=area,
        combustion_ids=combustion,
        complete=result.complete,
        finished_at_utc=_now(),
    )
    _write_json(snapshot / MANIFEST, manifest)
    if result.complete:
        (root / LATEST).write_text(snapshot.name + "\n", encoding="utf-8")
    result.drift = drift_against(previous_snapshot(root, snapshot), manifest)
    return result


def latest_snapshot(root: Path | None = None) -> Path:
    """Path of the latest *complete* snapshot (raises if none)."""
    root = root or catalog_root()
    pointer = root / LATEST
    if not pointer.exists():
        raise FileNotFoundError(f"No complete catalog snapshot under {root}. Run `flamesafe catalog`.")
    return root / pointer.read_text(encoding="utf-8").strip()


def load_details(snapshot: Path | None = None) -> dict[str, dict[str, Any]]:
    """{psi_id: detail JSON} from a snapshot (default: latest)."""
    snapshot = snapshot or latest_snapshot()
    manifest = _load_manifest(snapshot)
    return {
        psi_id: json.loads((snapshot / f"{psi_id}.json").read_text(encoding="utf-8"))
        for psi_id in manifest.get("combustion_ids", [])
        if (snapshot / f"{psi_id}.json").exists()
    }
