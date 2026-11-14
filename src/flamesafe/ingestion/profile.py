"""DE-04 · Automatic format profiling of tabular files (CSV / XLSX / XLS).

Facts only — what is in the file, not what it means. Interpretation (measured vs computed vs log,
granularity, value for the project) is written by humans in the investigation profiles.

Handles the quirks seen in PSI files:
  * UTF-8 with/without BOM, cp1252 fallback (recorded);
  * ACME raw streams whose first line is a `key: value` metadata preamble before the real header;
  * side-by-side blocks separated by empty columns (publication CSVs);
  * trailing blank rows (counted separately from non-empty rows);
  * non-numeric tokens inside mostly numeric columns (`RAMP`, `#DIV/0!`, `21; 26.5; 40` ...).
"""

from __future__ import annotations

import csv
import io
import math
import re
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

MAX_PROFILE_ROWS = 50_000
MAX_COLUMNS = 250
UNIT_PAREN = re.compile(r"\(([^()]{1,40})\)\s*$")
UNIT_SEMI = re.compile(r";\s*([^;]{1,40})$")
KV_CELL = re.compile(r"^[^:]{1,60}:\s+\S")


# ----------------------------------------------------------------------------- cells
def _to_float(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return None if (isinstance(v, float) and math.isnan(v)) else float(v)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            f = float(s)
            return None if math.isnan(f) else f
        except ValueError:
            return None
    return None


def _is_empty(v: Any) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def _short(v: Any, n: int = 40) -> str:
    s = v.isoformat() if isinstance(v, (datetime, date, time)) else str(v)
    s = s.strip().replace("\n", " ").replace("|", "/")
    return s if len(s) <= n else s[: n - 1] + "…"


def parse_unit(header: str) -> str | None:
    h = (header or "").strip()
    m = UNIT_PAREN.search(h) or UNIT_SEMI.search(h)
    return m.group(1).strip() if m else None


def profile_column(name: str, values: list[Any]) -> dict[str, Any]:
    non_empty = [v for v in values if not _is_empty(v)]
    nums = [f for f in (_to_float(v) for v in non_empty) if f is not None]
    dts = [v for v in non_empty if isinstance(v, (datetime, date, time))]
    n = len(non_empty)
    num_frac = len(nums) / n if n else 0.0
    if n == 0:
        kind = "empty"
    elif num_frac >= 0.9:
        kind = "numeric"
    elif len(dts) / n >= 0.9:
        kind = "datetime"
    elif num_frac >= 0.5:
        kind = "mixed"
    else:
        kind = "text"
    col: dict[str, Any] = {
        "name": (name or "").strip(),
        "unit_in_header": parse_unit(name or ""),
        "kind": kind,
        "non_empty": n,
        "n_unique": len({_short(v, 200) for v in non_empty}),
        "examples": [_short(v) for v in list(dict.fromkeys(_short(v, 200) for v in non_empty))[:3]],
    }
    if nums:
        col["min"], col["max"] = min(nums), max(nums)
    if kind in ("numeric", "mixed"):
        tokens = Counter(_short(v) for v in non_empty if _to_float(v) is None and not isinstance(v, (datetime, date, time)))
        if tokens:
            col["non_numeric_tokens"] = dict(tokens.most_common(6))
    return col


def _blocks(header: list[Any]) -> int:
    """Number of contiguous groups of non-empty header cells."""
    groups, inside = 0, False
    for cell in header:
        if not _is_empty(cell) and not inside:
            groups += 1
        inside = not _is_empty(cell)
    return groups


def profile_rows(rows: list[list[Any]], header_idx: int) -> dict[str, Any]:
    header = rows[header_idx] if rows else []
    body = rows[header_idx + 1 :]
    width = max([len(header)] + [len(r) for r in body[:2000]]) if rows else 0
    width = min(width, MAX_COLUMNS)
    nonempty_rows = [r for r in body if any(not _is_empty(c) for c in r)]
    cols = []
    for j in range(width):
        name = header[j] if j < len(header) and not _is_empty(header[j]) else f"<col {j + 1}>"
        cols.append(profile_column(str(name), [r[j] if j < len(r) else None for r in nonempty_rows[:MAX_PROFILE_ROWS]]))
    return {
        "header_row": header_idx + 1,  # 1-based physical row
        "physical_rows": len(body),
        "nonempty_rows": len(nonempty_rows),
        "n_columns": width,
        "n_blocks": _blocks(header[:width]),
        "truncated_columns": max(0, max([len(header)] + [0]) - MAX_COLUMNS),
        "columns": cols,
    }


def guess_header_row(rows: list[list[Any]], scan: int = 15) -> int:
    """First row (within `scan`) that is mostly text and about as wide as the widest early row."""
    head = rows[:scan]
    widths = [sum(not _is_empty(c) for c in r) for r in head]
    if not widths or max(widths) == 0:
        return 0
    target = max(2, math.ceil(0.5 * max(widths)))
    for i, r in enumerate(head):
        cells = [c for c in r if not _is_empty(c)]
        if len(cells) >= target and sum(isinstance(c, str) and _to_float(c) is None for c in cells) >= 0.6 * len(cells):
            return i
    return 0


# ----------------------------------------------------------------------------- files
def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            text = raw.decode(enc)
            return text, ("utf-8" + ("-bom" if raw.startswith(b"\xef\xbb\xbf") else "")) if enc == "utf-8-sig" else enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


def profile_csv(path: Path) -> dict[str, Any]:
    text, encoding = read_text(path)
    try:
        dialect = csv.Sniffer().sniff(text[:20_000], delimiters=",;\t")
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ","
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    out: dict[str, Any] = {"format": "csv", "encoding": encoding, "delimiter": delimiter}
    preamble: dict[str, str] = {}
    start = 0
    if rows:
        first = [c for c in rows[0] if c.strip()]
        if first and sum(bool(KV_CELL.match(c.strip())) for c in first) >= 0.6 * len(first):
            for c in first:
                if ":" in c:
                    k, v = c.split(":", 1)
                    preamble[k.strip()] = v.strip()
            start = 1
    if preamble:
        out["metadata_preamble"] = preamble
    header_idx = start + guess_header_row(rows[start:])
    out.update(profile_rows(rows, header_idx))
    return out


def _sheet_rows_xlsx(ws) -> list[list[Any]]:
    rows = []
    for i, r in enumerate(ws.iter_rows(values_only=True)):
        if i >= MAX_PROFILE_ROWS + 20:
            break
        rows.append(list(r))
    while rows and all(_is_empty(c) for c in rows[-1]):
        rows.pop()
    return rows


def profile_workbook(path: Path) -> dict[str, Any]:
    sheets = []
    if path.suffix.lower() == ".xlsx":
        import warnings

        import openpyxl

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)  # unsupported Excel extensions (formatting only)
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            for ws in wb.worksheets:
                rows = _sheet_rows_xlsx(ws)
                sheets.append({"sheet": ws.title, "reported_dims": [ws.max_row, ws.max_column], "rows": rows})
        fmt = "xlsx"
    else:
        import xlrd

        wb = xlrd.open_workbook(path, on_demand=True)
        for i in range(wb.nsheets):
            sh = wb.sheet_by_index(i)
            rows = [sh.row_values(r) for r in range(min(sh.nrows, MAX_PROFILE_ROWS + 20))]
            sheets.append({"sheet": sh.name, "reported_dims": [sh.nrows, sh.ncols], "rows": rows})
        fmt = "xls"
    out_sheets = []
    for s in sheets:
        rows = s.pop("rows")
        prof = profile_rows(rows, guess_header_row(rows)) if rows else {"physical_rows": 0, "nonempty_rows": 0,
                                                                         "n_columns": 0, "columns": []}
        out_sheets.append({**s, **prof})
    return {"format": fmt, "n_sheets": len(out_sheets), "sheets": out_sheets}


def profile_file(path: Path) -> dict[str, Any]:
    ext = path.suffix.lower()
    try:
        if ext in (".csv", ".txt"):
            return profile_csv(path)
        if ext in (".xlsx", ".xls"):
            return profile_workbook(path)
        return {"format": ext.lstrip("."), "profiled": False, "reason": "non-tabular format"}
    except Exception as exc:  # report, never crash the whole profiling run
        return {"format": ext.lstrip("."), "profiled": False, "reason": f"{type(exc).__name__}: {exc}"}
