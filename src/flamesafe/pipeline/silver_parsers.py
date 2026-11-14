"""DE-07 · Family parsers bronze -> silver for the ADR-0002 MVP sources + a generic experimental-table parser (RQ5).

Each parser returns {table_name: (DataFrame, meta)}. Column specs are explicit so schema drift fails loudly.
Silver keeps source units in column names; gold (DE-08) converts to canonical units.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from flamesafe import config
from flamesafe.pipeline.silver import (
    Col,
    Issues,
    _is_blank,
    apply_spec,
    bronze_source,
    norm_header,
    parser,
    read_csv_rows,
    read_sheet_rows,
    snake,
    split_table,
    to_float,
    with_provenance,
)

IGNITION = {"yes": "yes", "no": "no", "flash": "flash"}
EXTINCTION = {"se": "self_extinguished", "ft": "flow_terminated"}
FLAME_TYPE = {"normal": "normal", "inverse": "inverse"}


def _csv_table(psi_id: str, file_name: str, spec: list[Col], table: str, issues: Issues,
               header_row: int = 1) -> tuple[pd.DataFrame, dict[str, Any]]:
    src = bronze_source(psi_id, file_name)
    rows, encoding = read_csv_rows(src.path)
    header, body, nums, blank = split_table(rows, header_row)
    df, colmap = apply_spec(body, header, nums, spec, table, issues)
    meta = {"sources": [file_name], "encoding": encoding, "physical_rows": len(rows) - header_row,
            "blank_rows_dropped": blank, "column_map": colmap}
    return with_provenance(df, src), meta


def _sheet_table(psi_id: str, file_name: str, sheet: str, spec: list[Col], table: str, issues: Issues,
                 header_row: int = 1, require: str | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    src = bronze_source(psi_id, file_name)
    rows = read_sheet_rows(src.path, sheet)
    header, body, nums, blank = split_table(rows, header_row)
    if require:  # keep only rows where a key column is present (sheets padded with formatted empty rows)
        j = [norm_header(h) for h in header].index(require)
        keep = [i for i, r in enumerate(body) if not _is_blank(r[j])]
        blank += len(body) - len(keep)
        body, nums = [body[i] for i in keep], [nums[i] for i in keep]
    df, colmap = apply_spec(body, header, nums, spec, table, issues)
    meta = {"sources": [f"{file_name}#{sheet}"], "physical_rows": len(rows) - header_row,
            "blank_rows_dropped": blank, "column_map": colmap}
    return with_provenance(df, src), meta


# ============================================================================ PSI-159 · ACME CFI-G
CFIG_NORMAL = [
    Col("Flame Type", "flame_type", "category", FLAME_TYPE),
    Col("Day", "test_day", "int"),
    Col("Fuel", "fuel", "category"),
    Col("Test", "test_id", "id"),
    Col("Cool flame?", "cool_flame_raw", "str"),
    Col("XO2 before test", "xo2_before", "float"),
    Col("XO2 after test", "xo2_after", "float"),
    Col("approx p (bar)", "p_bar_approx", "float", unit_header="bar"),
    Col("Xf", "x_fuel", "float"),
    Col("mHC (mg/s)", "m_hc_mg_s", "float", unit_header="mg/s"),
    Col("TFP", "tfp", "bool_yesno", note="acronym not expanded in source"),
    Col("Tad (K)", "tad_k", "float", unit_header="K", note="computed by source"),
    Col("Zst", "zst", "float", note="computed by source"),
    Col("Hot ignition", "ignition_outcome", "category", IGNITION),
    Col("burn time (sec)", "burn_time_s", "float", unit_header="s"),
    Col("Self-ext or flow term", "extinction_mode", "category", EXTINCTION),
    Col("Peak burner T (C )", "peak_burner_t_c", "float", unit_header="C"),
    Col("Comments", "comments", "text"),
]

CFIG_INVERSE = [
    Col("Flame Type", "flame_type", "category", FLAME_TYPE),
    Col("Day", "test_day", "int"),
    Col("Fuel", "fuel", "category"),
    Col("Test", "test_id", "id"),
    Col("Xf before test", "x_fuel_before", "float"),
    Col("Xf after test", "x_fuel_after", "float"),
    Col("approx p (bar)", "p_bar_approx", "float", unit_header="bar"),
    Col("XO2", "xo2", "float"),
    Col("HC burnrate (mg/s)", "m_hc_mg_s", "float", unit_header="mg/s"),
    Col("O2 flow rate (mg/s)", "m_o2_mg_s", "float", unit_header="mg/s"),
    Col("TFP", "tfp", "bool_yesno"),
    Col("Tad (K)", "tad_k", "float", unit_header="K", note="computed by source"),
    Col("Zst", "zst", "float", note="computed by source"),
    Col("Hot ignition", "ignition_outcome", "category", IGNITION),
    Col("burn time (sec)", "burn_time_s", "float", unit_header="s"),
    Col("Self -ext or flow term", "extinction_mode", "category", EXTINCTION),
    Col("Peak burner Temp (C)", "peak_burner_t_c", "float", unit_header="C"),
    Col("Peak burner temp (K)", "peak_burner_t_k", "float", unit_header="K"),
    Col("Color", "color", "category"),
    Col("Comments", "comments", "text"),
]


@parser("psi159_cfig")
def parse_psi159(issues: Issues):
    return {
        "psi159__normal_flames": _csv_table("PSI-159", "PSI-159_Experimental table_CFI-G_Normal Flames.csv",
                                            CFIG_NORMAL, "psi159__normal_flames", issues),
        "psi159__inverse_flames": _csv_table("PSI-159", "PSI-159_Experimental table_CFI-G_Inverse Flames.csv",
                                             CFIG_INVERSE, "psi159__inverse_flames", issues),
    }


# ============================================================================ PSI-10 · ACME Flame Design
FD_NORMAL = [
    Col("Flame Type", "flame_type", "category", FLAME_TYPE),
    Col("Day", "test_day", "int"),
    Col("Fuel", "fuel", "category"),
    Col("Test", "test_id", "id"),
    Col("Xfuel", "x_fuel", "float"),
    Col("mfuel (mg/s)", "m_fuel_mg_s", "float", unit_header="mg/s"),
    Col("mN2 (mg/s)", "m_n2_mg_s", "float", unit_header="mg/s"),
    Col("mtot (mg/s)", "m_total_mg_s", "float", unit_header="mg/s"),
    Col("XO2 (init)", "xo2_init", "float"),
    Col("XO2 (final)", "xo2_final", "float"),
    Col("pinit (atm)", "p_init_atm", "float", unit_header="atm"),
    Col("pfinal (atm)", "p_final_atm", "float", unit_header="atm"),
    Col("pmean (atm)", "p_mean_atm", "float", unit_header="atm"),
    Col("mean Zst", "zst", "float", note="computed by source"),
    Col("Tad (K)", "tad_k", "float", unit_header="K", note="computed by source"),
]
FD_INVERSE = [
    Col("Flame Type", "flame_type", "category", FLAME_TYPE),
    Col("Day", "test_day", "int"),
    Col("Test", "test_id", "id"),
    Col("XO2", "xo2", "float"),
    Col("mO2 (mg/s)", "m_o2_mg_s", "float", unit_header="mg/s"),
    Col("mN2 (mg/s)", "m_n2_mg_s", "float", unit_header="mg/s"),
    Col("mtot (mg/s)", "m_total_mg_s", "float", unit_header="mg/s"),
    Col("XC2H4 initial", "x_c2h4_init", "float"),
    Col("XC2H4 final", "x_c2h4_final", "float"),
    Col("pinit (atm)", "p_init_atm", "float", unit_header="atm"),
    Col("pfinal (atm)", "p_final_atm", "float", unit_header="atm"),
    Col("pmean (atm)", "p_mean_atm", "float", unit_header="atm"),
    Col("mean Zst", "zst", "float", note="computed by source"),
    Col("Tad (K)", "tad_k", "float", unit_header="K", note="computed by source"),
]


@parser("psi10_flame_design")
def parse_psi10(issues: Issues):
    return {
        "psi10__normal_flames": _csv_table("PSI-10", "PSI-10_Experimental table_Flame Design_Normal Flame.csv",
                                           FD_NORMAL, "psi10__normal_flames", issues),
        "psi10__inverse_flames": _csv_table("PSI-10", "PSI-10_Experimental table_Flame Design_Inverse Flame.csv",
                                            FD_INVERSE, "psi10__inverse_flames", issues),
    }


# ============================================================================ ACME Chamber Calculator · EventData
_MFC = "ACME MFCs (Standard Liters - 0 DegC, 760 Torr)"
_PCT = "Finish Mixture (Percent)"
EVENTDATA = [
    Col("Operation|OP", "op", "str"),
    Col("Operation|Ignite", "ignite", "bool_yesno", note="operational decision (Notes sheet)"),
    Col("Operation|TPID", "tpid", "id"),
    Col("Time|Tstart (GMT)", "t_start_gmt", "date", date_formats=("%Y-%m-%d %H:%M:%S",)),
    Col("Time|Tend (GMT)", "t_end_gmt", "date", date_formats=("%Y-%m-%d %H:%M:%S",)),
    Col(f"{_MFC}|Diluent", "mfc_diluent_sl", "float", unit_header="standard liters"),
    Col(f"{_MFC}|Oxygen", "mfc_oxygen_sl", "float", unit_header="standard liters"),
    Col(f"{_MFC}|Nitrogen", "mfc_nitrogen_sl", "float", unit_header="standard liters"),
    Col(f"{_MFC}|Fuel", "mfc_fuel_sl", "float", unit_header="standard liters"),
    Col("Chamber Pressure|Pstart (psia)", "p_start_psia", "float", unit_header="psia"),
    Col("Chamber Pressure|Pend (psia)", "p_end_psia", "float", unit_header="psia"),
    Col("Event|Source-ID (SID)", "sid", "str"),
    Col("Event|Type", "event_type", "category"),
    Col("Fuel|Fuel Type", "fuel_type", "category"),
    Col("Igniter|Igniter Wattage", "igniter_w", "float", unit_header="W"),
    Col("Igniter|Igniter On Time (ms)", "igniter_on_ms", "float", unit_header="ms"),
    Col("PI|Burn Fraction", "burn_fraction", "float"),
    *[Col(f"{_PCT}|_{g}", f"finish_pct_{g.lower()}", "float", unit_header="percent")
      for g in ("O2", "He", "CO2", "N2", "H20", "Ethylene", "Methane", "Propane", "Butane", "Ethane", "H2")],
]


def _eventdata(psi_id: str, files: list[str], table: str, issues: Issues):
    frames, sources, physical, blank_total, colmap = [], [], 0, 0, {}
    for fn in files:
        src = bronze_source(psi_id, fn)
        rows = read_sheet_rows(src.path, "EventData")
        groups = pd.Series([norm_header(c) or None for c in rows[1]]).ffill().fillna("").tolist()
        header = [f"{g}|{norm_header(n)}" if norm_header(n) else "" for g, n in zip(groups, rows[2], strict=False)]
        _, body, nums, blank = split_table(rows, header_row=3, skip_after_header=1)  # row 4 = telemetry tags
        df, colmap = apply_spec(body, header, nums, EVENTDATA, table, issues, keep_unmapped=False)
        frames.append(with_provenance(df, src))
        sources.append(f"{fn}#EventData")
        physical += len(rows) - 4
        blank_total += blank
    df = pd.concat(frames, ignore_index=True)
    return df, {"sources": sources, "physical_rows": physical, "blank_rows_dropped": blank_total,
                "column_map": colmap, "note": "only spec columns kept (start/delta/finish SL mixtures dropped)"}


@parser("acme_eventdata")
def parse_eventdata(issues: Issues):
    man = pd.read_csv(config.ROOT / "docs" / "02_data_engineering" / "acquisition_manifest.csv")
    out = {}
    for psi_id in ("PSI-10", "PSI-159"):
        files = man[(man.psi_id == psi_id) & man.file_name.str.contains("Chamber Calculator")].file_name.tolist()
        table = f"{psi_id.lower().replace('-', '')}__eventdata"
        out[table] = _eventdata(psi_id, files, table, issues)
    return out


# ============================================================================ PSI-69 · FLEX
FLEX = [
    Col("FLEX Test #", "test_id", "id"),
    Col("FLEX Identifier", "flex_identifier", "str"),
    Col("Test Date", "test_date", "date", date_formats=("%m/%d/%Y", "%m/%d/%y")),
    Col("Test GMT", "test_gmt", "str"),
    Col("Fuel", "fuel", "category"),
    Col("Ambient pressure; mmHg", "p_ambient_mmhg", "float", unit_header="mmHg"),
    Col(r"re:^O\S* initial ambient composition", "x_o2", "float", unit_header="mole fraction",
        note="source header lost the subscript ('O' = O2)"),
    Col(r"re:^N\S* initial ambient composition", "x_n2", "float", unit_header="mole fraction"),
    Col(r"re:^CO\S* initial ambient composition", "x_co2", "float", unit_header="mole fraction",
        note="source header lost the subscript ('CO' = CO2)"),
    Col(r"re:^He initial ambient composition", "x_he", "float", unit_header="mole fraction"),
    Col("Droplet initial diameter; mm", "d0_mm", "float", unit_header="mm"),
    Col("Visible flame extinction diameter; mm", "d_ext_visible_mm", "float", unit_header="mm"),
    Col("Burning rate; mm", "burning_rate_k", "float", unit_header="mm",
        note="header says mm; presumed K in mm2/s — unverified (R-DE-05b)"),
    Col("Burn time; s", "burn_time_s", "float", unit_header="s"),
    Col("Test end", "test_end", "category", {"extinction": "extinction", "disruption": "disruption",
                                             "completion": "completion"}),
]


@parser("psi69_flex")
def parse_psi69(issues: Issues):
    df, meta = _csv_table("PSI-69", "PSI-69_Experimental table_FLEX.csv", FLEX, "psi69__flex_droplets", issues)
    bad_p = df["p_ambient_mmhg"].le(0).sum()
    if bad_p:
        issues.add("warning", "psi69__flex_droplets", f"{bad_p} row(s) with ambient pressure <= 0 mmHg (physically impossible)")
    return {"psi69__flex_droplets": (df, meta)}


# ============================================================================ PSI-39 · CFI DataSummary
CFI_FILE = "PSI-39_Science Documents_CFI_DataSummary_Spreadsheet_Jan2021.xlsx"
CFI_MASTER = [
    Col("Flex Number", "flex_number", "id"),
    Col("Test Date", "test_date", "date", date_formats=("%d-%b-%y",)),
    Col("Local Time", "local_time", "str"),
    Col("CIR", "cir_id", "str"),
    Col("Pressure", "pressure_raw", "str", note="text with unit, parsed to p_atm"),
    Col("Oxygen", "x_o2", "float"),
    Col("Nitrogen", "x_n2", "float"),
    Col("Helium", "x_he", "float"),
    Col("Fiber", "fiber", "bool_yesno"),
    Col("Fuel", "fuel", "str"),
]
CFI_DATA = [
    Col("Flex Number", "flex_number", "id"),
    Col("D0 ( mm )", "d0_mm", "float", unit_header="mm"),
    Col("Dext, hot ( mm )", "d_ext_hot_mm", "float", unit_header="mm"),
    Col("khot ( mm^2/s )", "k_hot_mm2_s", "float", unit_header="mm^2/s"),
    Col("kcool ( mm^2/s )", "k_cool_mm2_s", "float", unit_header="mm^2/s"),
    Col("Dext,cool ( mm )", "d_ext_cool_mm", "float", unit_header="mm"),
    Col("Pressure (atm)", "p_atm", "float", unit_header="atm"),
    Col("Reignitions", "reignitions", "int"),
    Col("Extrap CF?", "extrapolated_cf", "int"),
    Col("HF Burn Time", "hf_burn_time", "float", note="no unit in header (presumably s)"),
    Col("Peak HF Rad", "peak_hf_rad", "float", note="no unit in header"),
    Col("Peak Water Vapor Rad", "peak_water_vapor_rad", "float", note="no unit in header"),
    Col("Rad Ratio", "rad_ratio", "float"),
    Col("2.5mm rad", "rad_2p5mm", "float"),
    Col("2.5mm narrow", "narrow_2p5mm", "float"),
    Col("CF Rad Ratio", "cf_rad_ratio", "float"),
    Col("2.5mm CF", "cf_2p5mm", "float"),
    Col("2.5mm time", "time_2p5mm", "float"),
    Col("Actual D", "actual_d", "float"),
    Col("Completed Analysis?", "analysis_complete", "bool_yesno"),
]
_P_ATM = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*atm\s*$", re.IGNORECASE)


@parser("psi39_cfi")
def parse_psi39(issues: Issues):
    master, mmeta = _sheet_table("PSI-39", CFI_FILE, "Master Sheet", CFI_MASTER, "psi39__cfi_tests", issues,
                                 require="Flex Number")
    parsed = master["pressure_raw"].map(lambda s: float(m.group(1)) if isinstance(s, str) and (m := _P_ATM.match(s)) else None)
    master.insert(master.columns.get_loc("pressure_raw") + 1, "p_atm", parsed)
    if master["pressure_raw"].notna().sum() != parsed.notna().sum():
        issues.add("warning", "psi39__cfi_tests", "some Pressure values not of the form '<number> atm'")
    data, dmeta = _sheet_table("PSI-39", CFI_FILE, "DATA", CFI_DATA, "psi39__cfi_results", issues, require="Flex Number")
    orphan = set(data["flex_number"]) - set(master["flex_number"])
    if orphan:
        issues.add("warning", "psi39__cfi_results", f"{len(orphan)} flex_number(s) without Master Sheet conditions: {sorted(orphan)[:5]}")
    return {"psi39__cfi_tests": (master, mmeta), "psi39__cfi_results": (data, dmeta)}


# ============================================================================ PSI-117 · figure CSVs (ground)
ROLE_EXPT = re.compile(r"\b(expt|exp|experiment\w*)\b|_expt\b", re.IGNORECASE)
ROLE_MODEL = re.compile(r"\b(model|sim|simulation)\b|_model\b", re.IGNORECASE)
ROLE_ERRBAR = re.compile(r"error\s*bar", re.IGNORECASE)


def _role(*texts: str) -> str:
    joined = " ".join(t for t in texts if t)
    if ROLE_ERRBAR.search(joined):
        return "error_bar"
    if ROLE_MODEL.search(joined):
        return "model"
    if ROLE_EXPT.search(joined):
        return "experiment"
    return "unknown"


def figure_points(rows: list[list[str]], data_file: str) -> list[dict[str, Any]]:
    """Long-format points from side-by-side blocks separated by empty header cells."""
    header = [norm_header(h) for h in rows[0]]
    blocks, cur = [], []
    for j, h in enumerate(header + [""]):
        if h:
            cur.append(j)
        elif cur:
            blocks.append(cur)
            cur = []
    out = []
    for b, cols in enumerate(blocks):
        names = [header[j] for j in cols]
        body = [(i + 1, r) for i, r in enumerate(rows) if i > 0 and any(j < len(r) and str(r[j]).strip() for j in cols)]
        if not body:
            continue
        numeric = [j for j in cols if sum(to_float(r[j]) is not None for _, r in body if j < len(r)) >= 0.5 * len(body)]
        label_cols = [j for j in cols if j not in numeric]
        if len(numeric) < 2:
            continue
        x_j, y_js = numeric[0], numeric[1:]
        block_label = names[0] if cols[0] in label_cols else ""
        row_label = ""
        for phys_row, r in body:
            # a row label (e.g. "Expt", "Sim") applies to the following unlabeled rows of the same block
            if label_cols and label_cols[0] < len(r) and str(r[label_cols[0]]).strip():
                row_label = str(r[label_cols[0]]).strip()
            x = to_float(r[x_j]) if x_j < len(r) else None
            for yj in y_js:
                y = to_float(r[yj]) if yj < len(r) else None
                if x is None or y is None:
                    continue
                out.append({"data_file": data_file, "block": b + 1, "block_label": block_label or None,
                            "row_label": row_label or None, "role": _role(block_label, row_label, header[yj]),
                            "x_name": header[x_j], "x": x, "y_name": header[yj], "y": y, "source_row": phys_row})
    return out


@parser("psi117_figures")
def parse_psi117(issues: Issues):
    man = pd.read_csv(config.ROOT / "docs" / "02_data_engineering" / "acquisition_manifest.csv")
    files = man[(man.psi_id == "PSI-117") & man.file_name.str.endswith(".csv")].file_name.tolist()
    points, sources = [], []
    for fn in files:
        src = bronze_source("PSI-117", fn)
        rows, _ = read_csv_rows(src.path)
        pts = figure_points(rows, fn.replace("PSI-117_Analyzed Data_", "").removesuffix(".csv"))
        if not pts:
            issues.add("warning", "psi117__figure_points", f"no numeric x/y blocks found in {fn}")
        for p in pts:
            p.update(source_file=fn, source_sha256=src.sha256)
        points += pts
        sources.append(fn)
    df = pd.DataFrame(points)
    df.insert(0, "psi_id", "PSI-117")
    n_unknown = int((df["role"] == "unknown").sum())
    if n_unknown:
        issues.add("info", "psi117__figure_points", f"{n_unknown} points with role=unknown (time histories without Expt/Model label)")

    # ReadMe: several stacked sub-tables, each with its own header row; the 7th column changes meaning (XO3 vs XHe)
    rsrc = bronze_source("PSI-117", "PSI-117_Analyzed Data_ReadMe_List_of_Data.xlsx")
    rrows = read_sheet_rows(rsrc.path)
    recs, current = [], None
    for i, r in enumerate(rrows, start=1):
        cells = [norm_header(c) for c in r]
        if "Fuel" in cells and "P (atm)" in cells:
            # later sub-table headers omit the trailing "Data File / Reference / figure" labels: inherit them
            if current is not None:
                cells = [c or (current[k] if k >= 7 and k < len(current) else c) for k, c in enumerate(cells)]
            current = cells
            continue
        if current is None or all(not c for c in cells):
            continue
        rec = {snake(h): (c or None) for h, c in zip(current, cells, strict=False) if h}
        recs.append({"fuel": rec.get("fuel"), "d0_mm_raw": rec.get("do_mm"), "p_atm_raw": rec.get("p_atm"),
                     "xo2_raw": rec.get("xo2"), "xn2_raw": rec.get("xn2"),
                     "third_component": next((h for h in current[6:7] if h), None),
                     "third_component_raw": cells[6] if len(cells) > 6 else None,
                     "data_file": rec.get("data_file"), "doi": (rec.get("reference") or "").replace("https://doi.org/", "").strip() or None,
                     "figure": cells[10] if len(cells) > 10 else None, "source_row": i})
    readme = pd.DataFrame(recs)
    readme.insert(0, "psi_id", "PSI-117")
    readme["source_file"], readme["source_sha256"] = rsrc.file_name, rsrc.sha256
    pct = readme["xn2_raw"].map(lambda v: (to_float(v) or 0) > 1).sum()
    if pct:
        issues.add("warning", "psi117__readme", f"{pct} row(s) with XN2 > 1 (percent, not mole fraction) — kept raw")
    return {
        "psi117__figure_points": (df, {"sources": sources, "column_map": {}, "note": "long format; model points are not measurements"}),
        "psi117__readme": (readme, {"sources": [rsrc.file_name], "column_map": {}}),
    }


# ============================================================================ generic · all experimental tables (RQ5)
@parser("experimental_tables_generic")
def parse_experimental_tables(issues: Issues):
    man = pd.read_csv(config.ROOT / "docs" / "02_data_engineering" / "acquisition_manifest.csv")
    out = {}
    for r in man[man.list_source == "experimentalTable"].itertuples():
        slug = snake(r.file_name.split("Experimental table_", 1)[-1].removesuffix(".csv"))
        table = f"et__{r.psi_id.lower().replace('-', '')}__{slug}"
        src = bronze_source(r.psi_id, r.file_name)
        rows, encoding = read_csv_rows(src.path)
        header, body, nums, blank = split_table(rows, 1)
        spec, seen = [], set()
        for j, h in enumerate(header):
            h = norm_header(h)
            if not h:
                continue
            vals = [x[j] for x in body if j < len(x) and not _is_blank(x[j])]
            kind = "float" if vals and sum(to_float(v) is not None for v in vals) >= 0.5 * len(vals) else "str"
            name = snake(h)
            while name in seen:
                name += "_x"
            seen.add(name)
            spec.append(Col(h, name, kind))
        df, colmap = apply_spec(body, header, nums, spec, table, issues, keep_unmapped=False)
        out[table] = (with_provenance(df, src), {"sources": [r.file_name], "encoding": encoding,
                                                 "physical_rows": len(rows) - 1, "blank_rows_dropped": blank,
                                                 "column_map": colmap, "note": "generic typing (>=50% numeric -> float)"})
    return out
