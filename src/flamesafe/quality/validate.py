"""DE-09/DE-10 · Pipeline validation = the G2 gate, as code.

1. Contracts: pandera schemas for gold and silver MVP tables (+ provenance on every generic table).
2. Reconciliation: bronze non-blank rows == silver rows; silver rows == gold rows (per documented mapping).
3. No token -> 0: wherever silver flagged a token, the same-named gold column is NULL (never 0 or any value).
4. Dictionary coverage: every gold column is documented in DATA_DICTIONARY.md (and nothing documented is missing).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pandera.pandas as pa

from flamesafe import config
from flamesafe.quality.schemas import GENERIC_ET, GOLD, SILVER

GOLD_FROM_SILVER = {
    "gas_flame_tests": ["psi159__normal_flames", "psi159__inverse_flames", "psi10__normal_flames", "psi10__inverse_flames"],
    "droplet_tests": ["psi69__flex_droplets", "psi39__cfi_tests"],
    "droplet_reference_points": ["psi117__figure_points"],
}
DICTIONARY = config.ROOT / "docs" / "02_data_engineering" / "DATA_DICTIONARY.md"


def _dirs() -> tuple[Path, Path]:
    base = config.data_dir()
    return base / "silver" / "tables", base / "gold"


# ----------------------------------------------------------------------------- 1. contracts
def check_schema(df: pd.DataFrame, schema: pa.DataFrameSchema) -> dict[str, Any]:
    try:
        schema.validate(df, lazy=True)
        return {"ok": True, "n_failures": 0}
    except pa.errors.SchemaErrors as exc:
        fc = exc.failure_cases[["column", "check", "failure_case"]].astype(str)
        # one entry per (column, check) with a count and an example — dataframe-level checks repeat per column
        summary = (fc.groupby(["column", "check"], dropna=False)
                   .agg(n=("failure_case", "size"), example=("failure_case", "first")).reset_index()
                   .sort_values("n", ascending=False).head(25).to_dict("records"))
        return {"ok": False, "n_failures": int(len(fc)), "failures": summary}


def validate_contracts(silver_dir: Path, gold_dir: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, schema in GOLD.items():
        out[f"gold.{name}"] = check_schema(pd.read_parquet(gold_dir / f"{name}.parquet"), schema)
    for name, schema in SILVER.items():
        out[f"silver.{name}"] = check_schema(pd.read_parquet(silver_dir / f"{name}.parquet"), schema)
    for path in sorted(silver_dir.glob("et__*.parquet")):
        out[f"silver.{path.stem}"] = check_schema(pd.read_parquet(path), GENERIC_ET)
    return out


# ----------------------------------------------------------------------------- 2. reconciliation
def reconcile(silver_dir: Path, gold_dir: Path) -> list[dict[str, Any]]:
    rows = []
    report = json.loads((silver_dir.parent / "_reports" / "tables_parse_report.json").read_text(encoding="utf-8"))
    for table, meta in report["tables"].items():
        if "physical_rows" in meta and "blank_rows_dropped" in meta:
            expected = meta["physical_rows"] - meta["blank_rows_dropped"]
            rows.append({"stage": "bronze->silver", "table": table, "expected": expected, "actual": meta["rows"],
                         "ok": expected == meta["rows"]})
    for gold_table, sources in GOLD_FROM_SILVER.items():
        keys = ["psi_id", "source_file", "source_row"]
        inputs = pd.concat([pd.read_parquet(silver_dir / f"{s}.parquet") for s in sources])
        output = pd.read_parquet(gold_dir / f"{gold_table}.parquet")
        expected, actual = len(inputs), len(output)
        identity_ok = Counter(inputs[keys].itertuples(index=False, name=None)) == Counter(
            output[keys].itertuples(index=False, name=None)
        )
        rows.append({"stage": "silver->gold", "table": gold_table, "expected": expected, "actual": actual,
                     "ok": expected == actual and identity_ok, "identity_ok": identity_ok, "sources": sources})
    return rows


# ----------------------------------------------------------------------------- 3. token -> NULL
def tokens_never_valued(silver_dir: Path, gold_dir: Path) -> list[dict[str, Any]]:
    """For every silver `<col>__flag` with a same-named gold column, the gold value must be NULL on flagged rows."""
    results = []
    for gold_table, sources in GOLD_FROM_SILVER.items():
        g = pd.read_parquet(gold_dir / f"{gold_table}.parquet")
        for s in sources:
            sv = pd.read_parquet(silver_dir / f"{s}.parquet")
            for flag in [c for c in sv.columns if c.endswith("__flag")]:
                col = flag[: -len("__flag")]
                if col not in g.columns:
                    continue
                flagged = sv.loc[sv[flag].notna(), ["source_file", "source_row"]]
                if flagged.empty:
                    continue
                m = flagged.merge(g[["source_file", "source_row", col]], on=["source_file", "source_row"], how="left")
                bad = int(m[col].notna().sum())
                results.append({"gold_table": gold_table, "silver_table": s, "column": col,
                                "flagged_rows": len(flagged), "valued_in_gold": bad, "ok": bad == 0})
    return results


# ----------------------------------------------------------------------------- 4. dictionary coverage
def documented_columns(text: str) -> dict[str, set[str]]:
    """Backticked names in the first cell of table rows under each '### `table`' heading of the Gold section."""
    gold = text.split("## Gold", 1)[-1]
    out: dict[str, set[str]] = {}
    current = None
    for line in gold.splitlines():
        h = re.match(r"^###\s+`([a-z0-9_]+)`", line)
        if h:
            current = h.group(1)
            out[current] = set()
            continue
        if current and line.startswith("|") and not line.startswith("|---"):
            first = line.split("|")[1]
            out[current] |= set(re.findall(r"`([A-Za-z0-9_]+)`", first))
    return out


def dictionary_coverage(gold_dir: Path, dictionary: Path = DICTIONARY) -> list[dict[str, Any]]:
    docs = documented_columns(dictionary.read_text(encoding="utf-8"))
    res = []
    for table in GOLD:
        cols = set(pd.read_parquet(gold_dir / f"{table}.parquet").columns)
        doc = docs.get(table, set())
        res.append({"table": table, "undocumented": sorted(cols - doc), "documented_but_missing": sorted(doc - cols),
                    "ok": not (cols - doc) and not (doc - cols)})
    return res


# ----------------------------------------------------------------------------- runner
def run(write_summary: bool = True) -> dict[str, Any]:
    silver_dir, gold_dir = _dirs()
    contracts = validate_contracts(silver_dir, gold_dir)
    recon = reconcile(silver_dir, gold_dir)
    tokens = tokens_never_valued(silver_dir, gold_dir)
    coverage = dictionary_coverage(gold_dir)
    gate = {
        "contracts_ok": all(v["ok"] for v in contracts.values()),
        "reconciliation_ok": all(r["ok"] for r in recon),
        "tokens_never_valued_ok": all(t["ok"] for t in tokens),
        "dictionary_coverage_ok": all(c["ok"] for c in coverage),
    }
    report = {"validated_at": datetime.now().astimezone().isoformat(timespec="seconds"), "gate": gate,
              "passed": all(gate.values()), "contracts": contracts, "reconciliation": recon,
              "tokens_never_valued": tokens, "dictionary_coverage": coverage}
    rep_dir = gold_dir / "_reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    with open(rep_dir / "validation_report.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, default=str)
        fh.write("\n")
    if write_summary:  # committed evidence: counts and verdicts only, no data values
        summary = {
            "validated_at": report["validated_at"], "passed": report["passed"], "gate": gate,
            "contracts": {k: v["ok"] for k, v in contracts.items()},
            "reconciliation": [{k: r[k] for k in ("stage", "table", "expected", "actual", "ok")} for r in recon],
            "tokens_never_valued": [{k: t[k] for k in ("gold_table", "column", "flagged_rows", "valued_in_gold", "ok")} for t in tokens],
            "dictionary_coverage": coverage,
        }
        day = datetime.now().date().isoformat()
        path = config.ROOT / "docs" / "02_data_engineering" / "verification" / f"pipeline_validation_{day}.json"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(summary, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        report["summary_path"] = str(path)
    return report
