"""DE-07 · bronze -> silver framework: declarative column specs, typed coercion with flags, provenance.

Rules (docs/02_data_engineering/PIPELINE_MEDALLION.md §3):
  * non-numeric / non-parseable tokens -> NULL + `<col>__flag` with the original token (never 0);
  * original units are kept in silver column names (`_atm`, `_mmhg`, `_bar`, `_c`, `_mg_s` ...); canonical units are gold's job;
  * every row carries `psi_id`, `source_file`, `source_sha256`, `source_row` (1-based physical row in the source sheet/file);
  * a spec column missing from the source is an ERROR (schema drift); an unexpected source column is a WARNING (kept as text).
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from flamesafe import config
from flamesafe.ingestion.profile import read_text
from flamesafe.pipeline.promotion import promote_files, stage_files

KINDS = {"str", "text", "id", "int", "float", "bool_yesno", "category", "date"}


@dataclass(frozen=True)
class Col:
    source: str                     # normalized source header (exact match) or "re:<regex>"
    name: str                       # silver column name (snake_case, unit suffix)
    kind: str = "str"
    mapping: dict[str, Any] | None = None   # category: lower-case raw value -> canonical (unmapped -> NULL + flag)
    date_formats: tuple[str, ...] = ()
    unit_header: str | None = None  # unit as written in the source header (documentation)
    note: str = ""

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown kind {self.kind}")


@dataclass
class Issues:
    items: list[dict[str, str]] = field(default_factory=list)

    def add(self, level: str, table: str, issue: str) -> None:
        self.items.append({"level": level, "table": table, "issue": issue})

    @property
    def n_errors(self) -> int:
        return sum(i["level"] == "error" for i in self.items)


# ----------------------------------------------------------------------------- names & tokens
def norm_header(h: Any) -> str:
    return re.sub(r"\s+", " ", str(h)).strip() if h is not None and not (isinstance(h, float) and pd.isna(h)) else ""


def snake(h: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z]+", "_", h).strip("_").lower()
    return s or "col"


def missing_tokens() -> set[str]:
    return {t.strip().lower() for t in config.load("pipeline").get("missing_tokens", [])}


def _is_blank(v: Any) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and not v.strip())


def _as_str(v: Any) -> str | None:
    if _is_blank(v):
        return None
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return str(v).strip()


def to_float(v: Any) -> float | None:
    if _is_blank(v) or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        f = float(str(v).strip().replace("−", "-"))
        return None if pd.isna(f) else f
    except ValueError:
        return None


# ----------------------------------------------------------------------------- coercion
def coerce(values: list[Any], col: Col) -> tuple[list[Any], list[str | None]]:
    """Return (typed values, flags). flag = original token when a non-blank value could not be typed."""
    out, flags = [], []
    for v in values:
        flag = None
        if _is_blank(v):
            val = None
        elif col.kind in ("str", "text"):
            val = _as_str(v)
        elif col.kind == "id":
            val = re.sub(r"\s+", "", _as_str(v)).upper()
        elif col.kind in ("float", "int"):
            f = to_float(v)
            if f is None:
                val, flag = None, _as_str(v)
            elif col.kind == "int":
                if f.is_integer():
                    val = int(f)
                else:
                    val, flag = None, _as_str(v)
            else:
                val = f
        elif col.kind == "bool_yesno":
            s = _as_str(v).lower()
            val = True if s in ("yes", "y", "true") else False if s in ("no", "n", "false") else None
            flag = None if val is not None else _as_str(v)
        elif col.kind == "category":
            s = _as_str(v).lower()
            if col.mapping is None:
                val = None if s in missing_tokens() else s
                flag = _as_str(v) if val is None else None
            else:
                val = col.mapping.get(s)
                flag = None if val is not None else _as_str(v)
        elif col.kind == "date":
            if isinstance(v, (datetime, date)):
                val = pd.Timestamp(v)
            else:
                val = None
                for fmt in col.date_formats:
                    try:
                        val = pd.Timestamp(datetime.strptime(_as_str(v), fmt))
                        break
                    except ValueError:
                        continue
                flag = None if val is not None else _as_str(v)
        else:  # pragma: no cover
            raise ValueError(col.kind)
        out.append(val)
        flags.append(flag)
    return out, flags


def _match(col: Col, headers: list[str]) -> int | None:
    if col.source.startswith("re:"):
        rx = re.compile(col.source[3:])
        hits = [i for i, h in enumerate(headers) if rx.search(h)]
    else:
        hits = [i for i, h in enumerate(headers) if h == col.source]
    return hits[0] if len(hits) == 1 else (None if not hits else -1)


def apply_spec(rows: list[list[Any]], headers: list[Any], row_numbers: list[int], spec: list[Col],
               table: str, issues: Issues, keep_unmapped: bool = True) -> tuple[pd.DataFrame, dict[str, str]]:
    """Typed DataFrame (one column per spec entry, + __flag columns when needed) and {silver_col: source_header}."""
    hdr = [norm_header(h) for h in headers]
    data: dict[str, list[Any]] = {}
    colmap: dict[str, str] = {}
    used: set[int] = set()
    for col in spec:
        j = _match(col, hdr)
        if j is None:
            issues.add("error", table, f"spec column {col.source!r} not found in source headers")
            continue
        if j == -1:
            issues.add("error", table, f"spec column {col.source!r} matches several source headers")
            continue
        used.add(j)
        vals, flags = coerce([r[j] if j < len(r) else None for r in rows], col)
        data[col.name] = vals
        colmap[col.name] = hdr[j]
        if any(f is not None for f in flags):
            data[f"{col.name}__flag"] = flags
    for j, h in enumerate(hdr):
        if j in used or not h:
            continue
        if keep_unmapped and any(not _is_blank(r[j]) for r in rows if j < len(r)):
            name = snake(h)
            while name in data:
                name += "_x"
            data[name] = [_as_str(r[j]) if j < len(r) else None for r in rows]
            colmap[name] = h
            issues.add("warning", table, f"unexpected source column {h!r} kept as text `{name}`")
    df = pd.DataFrame(data)
    df.insert(0, "source_row", row_numbers)
    return df, colmap


# ----------------------------------------------------------------------------- readers
@dataclass
class Source:
    psi_id: str
    file_name: str
    path: Path
    sha256: str


def bronze_source(psi_id: str, file_name: str, root: Path | None = None) -> Source:
    root = root or config.data_dir() / "bronze" / "files"
    path = root / psi_id / file_name
    meta_path = path.with_name(path.name + ".meta.json")
    if not path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"bronze file missing: {psi_id}/{file_name} (run `flamesafe bronze`)")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return Source(psi_id, file_name, path, meta["sha256"])


def read_csv_rows(path: Path) -> tuple[list[list[str]], str]:
    text, encoding = read_text(path)
    return list(csv.reader(io.StringIO(text))), encoding


def read_sheet_rows(path: Path, sheet: str | int = 0) -> list[list[Any]]:
    df = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
    return df.where(pd.notna(df), None).values.tolist()


def split_table(rows: list[list[Any]], header_row: int, skip_after_header: int = 0) -> tuple[list[Any], list[list[Any]], list[int], int]:
    """header_row is 1-based. Returns header, non-blank data rows, their 1-based physical row numbers, n blank rows dropped."""
    header = rows[header_row - 1]
    body, nums, blank = [], [], 0
    for i in range(header_row + skip_after_header, len(rows)):
        if all(_is_blank(c) for c in rows[i]):
            blank += 1
            continue
        body.append(rows[i])
        nums.append(i + 1)
    return header, body, nums, blank


def with_provenance(df: pd.DataFrame, src: Source) -> pd.DataFrame:
    df = df.copy()
    df.insert(0, "psi_id", src.psi_id)
    df["source_file"] = src.file_name
    df["source_sha256"] = src.sha256
    return df


# ----------------------------------------------------------------------------- registry & runner
ParserFn = Callable[[Issues], dict[str, tuple[pd.DataFrame, dict[str, Any]]]]
REGISTRY: dict[str, ParserFn] = {}


def parser(name: str) -> Callable[[ParserFn], ParserFn]:
    def deco(fn: ParserFn) -> ParserFn:
        REGISTRY[name] = fn
        return fn
    return deco


def silver_tables_dir() -> Path:
    return config.data_dir() / "silver" / "tables"


def run(only: list[str] | None = None, out_dir: Path | None = None) -> dict[str, Any]:
    from flamesafe.pipeline import silver_parsers  # noqa: F401  (registers parsers)

    out_dir = out_dir or silver_tables_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    issues = Issues()
    tables: dict[str, Any] = {}
    with stage_files(out_dir.parent, "silver") as stage:
        for name, fn in REGISTRY.items():
            if only and name not in only:
                continue
            try:
                produced = fn(issues)
            except FileNotFoundError as exc:
                issues.add("error", name, str(exc))
                continue
            for table, (df, meta) in produced.items():
                df.to_parquet(stage / f"{table}.parquet", index=False)
                flags = [c for c in df.columns if c.endswith("__flag")]
                tables[table] = {"parser": name, "rows": len(df), "columns": len(df.columns),
                                 "flagged_values": {c[:-6]: int(df[c].notna().sum()) for c in flags}, **meta}
        if not issues.n_errors:
            promote_files(stage, out_dir)
    report = {
        "built_at_utc": datetime.now().astimezone().isoformat(timespec="seconds"),
        "tables": tables,
        "selected_parsers": only,
        "issues": issues.items,
        "n_errors": issues.n_errors,
        "n_warnings": sum(i["level"] == "warning" for i in issues.items),
    }
    rep_dir = out_dir.parent / "_reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    with open(rep_dir / "tables_parse_report.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, default=str)
        fh.write("\n")
    report["out_dir"] = str(out_dir)
    return report
