"""Bounded, parameterized, read-only queries. SQL identifiers never come from an LLM."""

import json
import threading
from collections import OrderedDict
from pathlib import Path
from time import monotonic

import duckdb

from flamesafe.rag.schemas import ToolRequest, ToolResult
from flamesafe.rag.utils import digest

TABLES = (
    "investigations",
    "publications",
    "gas_flame_tests",
    "droplet_tests",
    "droplet_reference_points",
)
GAS_NUMERIC = {
    "xo2": "mole fraction",
    "p_kpa": "kPa",
    "x_fuel": "mole fraction",
    "po2_kpa": "kPa (derived)",
    "m_fuel_mg_s": "mg/s",
    "m_o2_mg_s": "mg/s",
    "m_n2_mg_s": "mg/s",
    "hc_burnrate_mg_s": "mg/s",
    "burn_time_s": "s",
    "peak_burner_t_k": "K",
    "tad_k": "K (calculated)",
    "zst": "dimensionless (calculated)",
}
DROP_NUMERIC = {
    "p_kpa": "kPa",
    "x_o2": "mole fraction",
    "d0_mm": "mm",
    "burn_time_s": "s",
    "k_hot_mm2_s": "mm²/s",
    "k_cool_mm2_s": "mm²/s",
}
CATALOG_COLUMNS = "psi_id, acronym, title, hardware_family, access_status, n_gold_tests"


def records(con, sql, params=()):
    cursor = con.execute(sql, params)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


class DataTools:
    def __init__(self, bundle: Path, build_id: str, source_mode: str):
        self.bundle, self.build_id, self.source_mode = bundle, build_id, source_mode
        self._evidence = OrderedDict()
        self._lock = threading.Lock()

    def retained(self, evidence_id):
        """At most 256 results for one hour, scoped to this process/snapshot."""
        with self._lock:
            saved = self._evidence.get(evidence_id)
            return saved[1] if saved and monotonic() - saved[0] < 3600 else None

    def execute(self, request: ToolRequest) -> ToolResult:
        con = duckdb.connect(str(self.bundle / "query_snapshot.duckdb"), read_only=True)
        timer = threading.Timer(5, con.interrupt)
        try:
            con.execute("SET enable_external_access=false")
            con.execute("SET autoinstall_known_extensions=false")
            con.execute("SET autoload_known_extensions=false")
            con.execute("SET threads=1")
            con.execute("SET memory_limit='256MB'")
            timer.start()
            result = self._execute(con, request)
            with self._lock:
                self._evidence[result.evidence_id] = (monotonic(), result)
                self._evidence.move_to_end(result.evidence_id)
                while len(self._evidence) > 256:
                    self._evidence.popitem(last=False)
            return result
        finally:
            timer.cancel()
            timer.join() if timer.ident else None
            con.close()

    def _execute(self, con, request):
        name, args = request.tool, request.arguments
        table = {
            "find_investigations": "investigations",
            "get_investigation": "investigations",
            "find_publications": "publications",
            "summarize_gas_tests": "gas_flame_tests",
            "summarize_ignition_outcomes": "gas_flame_tests",
            "list_gas_tests": "gas_flame_tests",
            "summarize_droplet_tests": "droplet_tests",
            "summarize_reference_points": "droplet_reference_points",
            "get_variable_definition": "variable_definitions",
        }[name]
        if args.cohort != "raw_gold":
            if table != "gas_flame_tests":
                raise ValueError("Audited scopes apply only to gas tests.")
            available = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
            if "audited_gas" not in available:
                raise ValueError(
                    "This snapshot has no EventData audit; select raw_gold explicitly."
                )
            table = "audited_gas"
        allowed = {
            "investigations": {"psi_id", "text"},
            "publications": {"text"},
            "gas_flame_tests": {
                "campaign",
                "flame_type",
                "fuel",
                "psi_id",
                "test_id",
                "ignition_outcome",
            },
            "audited_gas": {
                "campaign",
                "flame_type",
                "fuel",
                "psi_id",
                "test_id",
                "ignition_outcome",
            },
            "droplet_tests": {"campaign", "fuel", "psi_id", "test_id"},
            "droplet_reference_points": {"fuel", "psi_id"},
            "variable_definitions": {"variable"},
        }[table]
        filters, params = [], []
        values = args.model_dump(exclude_none=True)
        for key in (
            "campaign",
            "flame_type",
            "fuel",
            "psi_id",
            "test_id",
            "ignition_outcome",
            "text",
        ):
            if key not in values:
                continue
            if key not in allowed:
                raise ValueError(f"Filter {key} is not applicable to {name}.")
            if key == "text":
                filters.append("contains(lower(title), lower(?))")
            else:
                filters.append(f'"{key}" = ?')
            params.append(values[key])
        if args.cohort != "raw_gold":
            filters.append("identity_status = 'unique'")
            if args.cohort == "audited_verified_dates":
                filters.append("timestamp_verified = true")
        where = " WHERE " + " AND ".join(filters) if filters else ""
        if name == "get_investigation" and not args.psi_id:
            raise ValueError("psi_id is required.")
        if name == "get_variable_definition":
            if not args.variable:
                raise ValueError("variable is required.")
            where, params = " WHERE variable = ?", [args.variable]
        count = con.execute(f"SELECT count(*) FROM {table}{where}", params).fetchone()[0]
        units, valid, missing = {}, {}, {}
        n_unique = n_ops = None
        warnings = [f"Snapshot mode: {self.source_mode}. Counts describe this snapshot only."]
        gas = table in {"gas_flame_tests", "audited_gas"}
        if gas or table == "droplet_tests":
            n_unique = con.execute(
                f"SELECT count(DISTINCT (psi_id, test_id)) FROM {table}{where}",
                params,
            ).fetchone()[0]
        if table == "audited_gas":
            n_ops = con.execute(
                f"SELECT count(DISTINCT operation_group) FROM {table}{where}", params
            ).fetchone()[0]
        if gas:
            warnings += [
                "CFI-G experimental ignition and Flame Design EventData labels are not equivalent.",
                "Normal and inverse conditions have different physical meanings.",
                "Flash and missing outcomes are not negative ignition.",
            ]
        if name == "summarize_ignition_outcomes":
            group = "campaign, flame_type, outcome_source, ignition_outcome"
            rows = records(
                con,
                f"SELECT {group}, count(*) AS n FROM {table}{where} GROUP BY {group} ORDER BY {group}",
                params,
            )
            nonnull = con.execute(
                f"SELECT count(ignition_outcome) FROM {table}{where}", params
            ).fetchone()[0]
            valid, missing = {"ignition_outcome": nonnull}, {"ignition_outcome": count - nonnull}
        elif name in {"summarize_gas_tests", "summarize_droplet_tests"}:
            mapping = GAS_NUMERIC if gas else DROP_NUMERIC
            variable = args.variable or ("xo2" if gas else "d0_mm")
            if variable not in mapping:
                raise ValueError(
                    "Unsupported variable or unverified units; consult the dictionary."
                )
            if gas and variable == "m_n2_mg_s" and args.campaign != "Flame Design":
                raise ValueError("m_n2_mg_s requires campaign='Flame Design'.")
            if gas and variable in {"m_fuel_mg_s", "m_o2_mg_s", "hc_burnrate_mg_s"}:
                expected = "normal" if variable == "m_fuel_mg_s" else "inverse"
                if args.flame_type != expected:
                    raise ValueError(f"{variable} requires flame_type='{expected}'.")
            group = "campaign, flame_type, fuel" if gas else "campaign, fuel"
            rows = records(
                con,
                f"SELECT {group}, count(*) AS n, count({variable}) AS n_valid, min({variable}) AS minimum, quantile_cont({variable}, 0.25) AS q1, median({variable}) AS median, quantile_cont({variable}, 0.75) AS q3, max({variable}) AS maximum FROM {table}{where} GROUP BY {group} ORDER BY {group}",
                params,
            )
            nv = sum(row["n_valid"] for row in rows)
            valid, missing, units = (
                {variable: nv},
                {variable: count - nv},
                {variable: mapping[variable]},
            )
            if variable == "burn_time_s":
                warnings.append(
                    "Flow termination is not natural extinction. Burn time is not evacuation time."
                )
        elif name == "summarize_reference_points":
            rows = records(
                con,
                f"SELECT psi_id, role, count(*) AS n FROM {table}{where} GROUP BY psi_id, role ORDER BY psi_id, role",
                params,
            )
            warnings.append(
                "Digitized points, including model curves, are not independent experiments."
            )
        else:
            select = {
                "find_investigations": CATALOG_COLUMNS,
                "get_investigation": CATALOG_COLUMNS
                + ", objective, approach, hypothesis, research_impacts",
                "find_publications": "doi, title, author_list, status, psi_ids",
                "list_gas_tests": "psi_id, test_id, campaign, flame_type, fuel, ignition_outcome, xo2, p_kpa, source_file, source_row",
                "get_variable_definition": "variable, table_name, definition, source_id",
            }[name]
            order = "variable, table_name" if table == "variable_definitions" else "1, 2"
            rows = records(
                con,
                f"SELECT {select} FROM {table}{where} ORDER BY {order} LIMIT ?",
                [*params, args.limit],
            )
            if count > len(rows):
                warnings.append("Row preview is truncated; n_rows reports the full filtered scope.")
        payload = {
            "request": request.model_dump(),
            "build": self.build_id,
            "rows": rows,
            "count": count,
        }
        result_hash = digest(payload)
        return ToolResult(
            evidence_id=f"tool-{result_hash}",
            tool_name=name,
            normalized_parameters=args.model_dump(),
            dataset_build_id=self.build_id,
            population_or_cohort=args.cohort,
            n_rows=count,
            n_unique_tests=n_unique,
            n_operations=n_ops,
            n_valid_by_variable=valid,
            n_missing_by_variable=missing,
            units=units,
            results=rows,
            warnings=warnings,
            provenance_reference=f"{self.build_id}/{table}",
            result_hash=result_hash,
        )

    def counts(self):
        manifest = json.loads((self.bundle / "manifest.json").read_text(encoding="utf-8"))
        return manifest["row_counts"]
