"""Selection-driven downloader with budget guardrails (base for DE-04 sampling and DE-06 acquisition).

Each file -> data/bronze/files/<PSI-ID>/<file_name>  +  <file_name>.meta.json sidecar:
    psi_id, file_name, list_source, source_url (unsigned API url), retrieved_at_utc,
    http_status, bytes, expected_bytes, size_matches, sha256
404s and other HTTP errors are recorded in the sidecar (no data file), never hidden.
Re-running skips files whose bytes still match the sidecar sha256.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from flamesafe import config
from flamesafe.ingestion.psi_client import PSIClient, PSIError


class BudgetError(ValueError):
    pass


@dataclass(frozen=True)
class FileRequest:
    psi_id: str
    file_name: str
    expected_bytes: int | None
    list_source: str  # "added" | "experimentalTable"
    reason: str = ""


def files_root() -> Path:
    return config.data_dir() / "bronze" / "files"


def local_path(req: FileRequest, root: Path | None = None) -> Path:
    return (root or files_root()) / req.psi_id / req.file_name


def _sidecar(path: Path) -> Path:
    return path.with_name(path.name + ".meta.json")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


# ----------------------------------------------------------------------------- selection
def requests_from_l2(cfg: dict[str, Any], silver_dir: Path) -> list[FileRequest]:
    """Resolve configs/l2_samples.yaml against the silver catalog. Unknown names raise (no silent typos)."""
    files = pd.read_parquet(silver_dir / "files.parquet")
    added = files[files["inventory"] == "added"].set_index(["psi_id", "file_name"])
    tables = pd.read_parquet(silver_dir / "experimental_tables.parquet")
    out: dict[tuple[str, str], FileRequest] = {}

    if cfg.get("include_experimental_tables"):
        for t in tables.itertuples():
            out[(t.psi_id, t.file_name)] = FileRequest(
                t.psi_id, t.file_name, int(t.listed_bytes), "experimentalTable", "experimental table")

    missing = []
    for psi_id, names in (cfg.get("samples") or {}).items():
        for name in names:
            if (psi_id, name) in out:
                continue
            if (psi_id, name) not in added.index:
                missing.append(f"{psi_id}: {name}")
                continue
            out[(psi_id, name)] = FileRequest(
                psi_id, name, int(added.loc[(psi_id, name), "file_bytes"]), "added", "L2 sample")
    if missing:
        raise KeyError("Not in the current `added` inventory:\n  " + "\n  ".join(missing))
    return sorted(out.values(), key=lambda r: (int(r.psi_id.split("-")[1]), r.file_name))


def check_budget(reqs: Iterable[FileRequest], max_total_mb: float, max_file_mb: float,
                 deny_extensions: Iterable[str] = ()) -> int:
    reqs = list(reqs)
    deny = {e.lower() for e in deny_extensions}
    problems = [f"{r.psi_id}/{r.file_name}: extension .{_ext(r.file_name)} denied" for r in reqs
                if _ext(r.file_name) in deny]
    problems += [f"{r.psi_id}/{r.file_name}: {r.expected_bytes / 1e6:.1f} MB > {max_file_mb} MB" for r in reqs
                 if (r.expected_bytes or 0) > max_file_mb * 1e6]
    total = sum(r.expected_bytes or 0 for r in reqs)
    if total > max_total_mb * 1e6:
        problems.append(f"total {total / 1e6:.1f} MB > {max_total_mb} MB")
    if problems:
        raise BudgetError("Download budget violated:\n  " + "\n  ".join(problems))
    return total


# ----------------------------------------------------------------------------- fetch
def fetch(
    reqs: Iterable[FileRequest],
    client: PSIClient | None = None,
    root: Path | None = None,
    progress: Callable[[FileRequest, str], None] | None = None,
) -> list[dict[str, Any]]:
    client = client or PSIClient()
    say = progress or (lambda *_: None)
    results = []
    for req in reqs:
        path = local_path(req, root)
        side = _sidecar(path)
        if path.exists() and side.exists():
            meta = json.loads(side.read_text(encoding="utf-8"))
            if meta.get("http_status") == 200 and meta.get("sha256") == _sha256_file(path):
                results.append({**meta, "action": "reused"})
                say(req, "reused")
                continue
        meta: dict[str, Any] = {
            **asdict(req),
            "source_url": client.url("download", psi_id=req.psi_id, filename=req.file_name),
            "retrieved_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        }
        try:
            res = client.download(req.psi_id, req.file_name, path)
            meta.update(http_status=200, bytes=res.bytes, sha256=res.sha256, content_type=res.content_type,
                        size_matches=(req.expected_bytes is None or res.bytes == req.expected_bytes))
            action = "fetched" if meta["size_matches"] else "fetched_size_mismatch"
        except PSIError as exc:
            meta.update(http_status=exc.status)
            action = f"http_{exc.status}"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(side, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(meta, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        results.append({**meta, "action": action})
        say(req, action)
    return results


def write_report(results: list[dict[str, Any]], name: str, root: Path | None = None) -> Path:
    root = (root or files_root()).parent / "_reports"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"acquisition_{name}.json"
    summary = {
        "written_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "n_requested": len(results),
        "n_ok": sum(r.get("http_status") == 200 for r in results),
        "n_size_mismatch": sum(r.get("size_matches") is False for r in results),
        "bytes": sum(r.get("bytes", 0) for r in results),
        "by_action": pd.Series([r["action"] for r in results]).value_counts().to_dict() if results else {},
        "files": results,
    }
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path
