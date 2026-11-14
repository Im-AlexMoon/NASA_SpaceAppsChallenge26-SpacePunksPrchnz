"""DE-08 · silver -> gold: harmonized, analysis-ready tables defined in DATA_DICTIONARY § Gold (DS-02 contract).

Gold tables (data/gold/*.parquet + data/gold/flamesafe.duckdb):
    gas_flame_tests           RQ1 · M1/M3   (CFI-G + Flame Design, ignition outcome joined from EventData)
    droplet_tests             RQ2 · M2      (FLEX + CFI)
    droplet_reference_points  M2 validation (PSI-117 figure points + ReadMe conditions)
    investigations            RQ5           (catalog + triage + hardware family + gold coverage)
    publications              RAG / dashboard (deduplicated by DOI)

Conversions only through flamesafe.physics.units. Nothing is imputed; documented derivations are explicit columns.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from flamesafe import config
from flamesafe.physics import units

QUALIFIER_TOKENS = {"RAMP", "RAMPED", "LOW O2"}
FUEL_CANON = {"c2h4": "ethylene", "c3h8": "propane", "ethylene": "ethylene", "ethane": "ethane", "propane": "propane",
              "butane": "butane", "methane": "methane", "methanol": "methanol", "heptane": "heptane",
              "farnesane": "farnesane"}


def gold_dir() -> Path:
    return config.data_dir() / "gold"


def _silver(name: str) -> pd.DataFrame:
    return pd.read_parquet(config.data_dir() / "silver" / "tables" / f"{name}.parquet")


def _col(df: pd.DataFrame, name: str) -> pd.Series:
    return df[name] if name in df.columns else pd.Series([None] * len(df), index=df.index, dtype=object)


def parse_fuel(raw: Any) -> tuple[str | None, float | None]:
    """'30% butane' -> ('butane', 30.0); 'C2H4' -> ('ethylene', 100.0); unknown names are kept lower-case."""
    if raw is None or (isinstance(raw, float) and np.isnan(raw)):
        return None, None
    s = str(raw).strip().lower()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*%\s*(.+)$", s)
    pct, name = (float(m.group(1)), m.group(2).strip()) if m else (100.0, s)
    return FUEL_CANON.get(name, name), pct


def _qualifier(df: pd.DataFrame) -> pd.Series:
    flags = [c for c in df.columns if c.endswith("__flag")]

    def pick(row):
        for c in flags:
            v = row[c]
            if isinstance(v, str) and v.strip().upper() in QUALIFIER_TOKENS:
                return v.strip().upper()
        return None
    return df.apply(pick, axis=1) if flags else pd.Series([None] * len(df), index=df.index)


def _ignited(outcome: pd.Series) -> pd.Series:
    return outcome.map({"yes": True, "no": False}).astype("boolean")


# ============================================================================ gas_flame_tests
def build_gas_flame_tests() -> tuple[pd.DataFrame, dict[str, Any]]:
    parts, checks = [], {}

    def frame(df: pd.DataFrame, **cols) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        for k, v in cols.items():
            out[k] = v
        out["qualifier"] = _qualifier(df)
        out["source_file"], out["source_row"] = df["source_file"], df["source_row"]
        return out

    # --- CFI-G (outcome in the experimental table) -------------------------------------------
    ev159 = _silver("psi159__eventdata")
    ev159 = ev159[ev159.op.isin(["TP", "INV_TP"])].drop_duplicates("tpid").set_index("tpid")["ignite"]
    for kind, t in (("normal", "psi159__normal_flames"), ("inverse", "psi159__inverse_flames")):
        df = _silver(t)
        fuel = df["fuel"].map(parse_fuel)
        normal = kind == "normal"
        part = frame(
            df, psi_id="PSI-159", campaign="CFI-G", test_id=df.test_id, test_day=df.test_day, flame_type=kind,
            fuel=fuel.map(lambda x: x[0]), fuel_dilution_pct=fuel.map(lambda x: x[1]),
            xo2=df.xo2_before if normal else df.xo2, xo2_final=df.xo2_after if normal else np.nan,
            x_fuel=df.x_fuel if normal else df.x_fuel_before,
            p_kpa=df.p_bar_approx.map(units.bar_to_kpa), p_source="approx p (bar)",
            m_fuel_mg_s=df.m_hc_mg_s if normal else np.nan,
            hc_burnrate_mg_s=np.nan if normal else df.m_hc_mg_s,
            m_o2_mg_s=np.nan if normal else df.m_o2_mg_s, m_n2_mg_s=np.nan, m_total_mg_s=np.nan,
            zst=df.zst, tad_k=df.tad_k,
            ignition_outcome=df.ignition_outcome, outcome_source="experimental_table",
            ignite_eventdata=df.test_id.map(ev159).astype("boolean"),
            extinction_mode=df.extinction_mode, burn_time_s=df.burn_time_s,
            cool_flame=_col(df, "cool_flame_raw").map(
                lambda s: True if isinstance(s, str) and s.lower().startswith("yes")
                else False if isinstance(s, str) and s.lower().startswith("no") else None).astype("boolean"),
            peak_burner_t_k=(df.peak_burner_t_c.map(units.celsius_to_kelvin) if normal
                             else df.peak_burner_t_k.fillna(df.peak_burner_t_c.map(units.celsius_to_kelvin))),
            tfp=df.tfp.astype("boolean"),
        )
        parts.append(part)

    # --- Flame Design (outcome from EventData TP / INV_TP) ------------------------------------
    ev10 = _silver("psi10__eventdata")
    ev10 = ev10[ev10.op.isin(["TP", "INV_TP"])]
    checks["psi10_eventdata_duplicate_tpid"] = int(ev10.tpid.duplicated().sum())
    ign10 = ev10.drop_duplicates("tpid").set_index("tpid")["ignite"]
    nrm, inv = _silver("psi10__normal_flames"), _silver("psi10__inverse_flames")
    for kind, df in (("normal", nrm), ("inverse", inv)):
        normal = kind == "normal"
        fuel = df["fuel"].map(parse_fuel) if normal else pd.Series([("ethylene", np.nan)] * len(df), index=df.index)
        ign = df.test_id.map(ign10).astype("boolean")
        p_atm = df.p_mean_atm.fillna(df.p_init_atm)
        parts.append(frame(
            df, psi_id="PSI-10", campaign="Flame Design", test_id=df.test_id, test_day=df.test_day, flame_type=kind,
            fuel=fuel.map(lambda x: x[0]), fuel_dilution_pct=fuel.map(lambda x: x[1]) if normal else np.nan,
            xo2=df.xo2_init if normal else df.xo2, xo2_final=df.xo2_final if normal else np.nan,
            x_fuel=df.x_fuel if normal else df.x_c2h4_init,
            p_kpa=p_atm.map(units.atm_to_kpa), p_source=np.where(df.p_mean_atm.notna(), "pmean (atm)", "pinit (atm)"),
            m_fuel_mg_s=df.m_fuel_mg_s if normal else np.nan, hc_burnrate_mg_s=np.nan,
            m_o2_mg_s=np.nan if normal else df.m_o2_mg_s, m_n2_mg_s=df.m_n2_mg_s, m_total_mg_s=df.m_total_mg_s,
            zst=df.zst, tad_k=df.tad_k,
            ignition_outcome=ign.map({True: "yes", False: "no"}),
            outcome_source=np.where(ign.notna(), "eventdata", "none"),
            ignite_eventdata=ign, extinction_mode=None, burn_time_s=np.nan, cool_flame=pd.NA,
            peak_burner_t_k=np.nan, tfp=pd.NA,
        ))
        checks[f"psi10_{kind}_outcome_joined"] = f"{int(ign.notna().sum())}/{len(df)}"

    g = pd.concat(parts, ignore_index=True)
    g["ignited"] = _ignited(g["ignition_outcome"])
    g["po2_kpa"] = g["xo2"] * g["p_kpa"]
    g["fuel_dilution_pct"] = g["fuel_dilution_pct"].astype(float)
    order = ["psi_id", "campaign", "test_id", "test_day", "flame_type", "fuel", "fuel_dilution_pct", "xo2", "xo2_final",
             "x_fuel", "p_kpa", "p_source", "po2_kpa", "m_fuel_mg_s", "hc_burnrate_mg_s", "m_o2_mg_s", "m_n2_mg_s",
             "m_total_mg_s", "zst", "tad_k", "ignited", "ignition_outcome", "outcome_source", "ignite_eventdata",
             "extinction_mode", "burn_time_s", "cool_flame", "peak_burner_t_k", "tfp", "qualifier", "source_file", "source_row"]
    g = g[order]
    for c in ("cool_flame", "tfp", "ignited", "ignite_eventdata"):
        g[c] = g[c].astype("boolean")

    cfig = g[(g.campaign == "CFI-G") & g.ignited.notna() & g.ignite_eventdata.notna()]
    checks["cfig_hot_ignition_vs_eventdata"] = {
        "compared": len(cfig), "agree": int((cfig.ignited == cfig.ignite_eventdata).sum()),
        "table_yes_eventdata_no": int((cfig.ignited & ~cfig.ignite_eventdata).sum()),
        "table_no_eventdata_yes": int((~cfig.ignited & cfig.ignite_eventdata).sum()),
    }
    return g, checks


# ============================================================================ droplet_tests
def build_droplet_tests() -> tuple[pd.DataFrame, dict[str, Any]]:
    checks: dict[str, Any] = {}
    flex = _silver("psi69__flex_droplets")
    p = flex.p_ambient_mmhg.map(units.mmhg_to_kpa)
    bad_p = flex.p_ambient_mmhg.le(0)
    f = pd.DataFrame({
        "psi_id": "PSI-69", "campaign": "FLEX", "test_id": flex.test_id, "test_date": flex.test_date,
        "fuel": flex.fuel.map(lambda s: parse_fuel(s)[0]), "fuel_blend": None,
        "p_kpa": p.where(~bad_p), "x_o2": flex.x_o2, "x_n2": flex.x_n2, "x_co2": flex.x_co2, "x_he": flex.x_he,
        "x_co2_inferred": False, "d0_mm": flex.d0_mm, "fiber": pd.NA, "test_end": flex.test_end,
        "d_ext_hot_mm": flex.d_ext_visible_mm, "d_ext_cool_mm": np.nan,
        "k_hot_mm2_s": np.nan, "flex_burning_rate_unverified": flex.burning_rate_k, "k_cool_mm2_s": np.nan,
        "burn_time_s": flex.burn_time_s, "reignitions": pd.NA, "analysis_complete": pd.NA,
        "quality_flags": np.where(bad_p, "pressure<=0 in source", None),
        "source_file": flex.source_file, "source_row": flex.source_row,
    })
    checks["flex_rows_pressure_le_0"] = int(bad_p.sum())

    tests, res = _silver("psi39__cfi_tests"), _silver("psi39__cfi_results")
    m = tests.merge(res, on="flex_number", how="left", suffixes=("", "_res"), validate="one_to_one")
    checks["cfi_pressure_mismatch_master_vs_data"] = int(((m.p_atm - m.p_atm_res).abs() > 1e-9).sum())
    blend = m.fuel.str.extract(r"^\[(?P<a>[\d.]+)\]/\[(?P<b>[\d.]+)\]\s*(?P<name>.+)$")
    fuel = np.where(blend["name"].notna(), blend["name"], m.fuel.map(lambda s: parse_fuel(s)[0] if s != "C12H26" else "C12H26"))
    fuel_blend = np.where(blend["a"].notna(),
                          (blend["a"].astype(float) * 100).round().astype("Int64").astype(str) + "/" +
                          (blend["b"].astype(float) * 100).round().astype("Int64").astype(str), None)
    total = m.x_o2 + m.x_n2 + m.x_he
    inferred = (total - 1).abs() <= 0.005
    c = pd.DataFrame({
        "psi_id": "PSI-39", "campaign": "CFI", "test_id": m.flex_number, "test_date": m.test_date,
        "fuel": fuel, "fuel_blend": fuel_blend, "p_kpa": m.p_atm.map(units.atm_to_kpa),
        "x_o2": m.x_o2, "x_n2": m.x_n2, "x_co2": np.where(inferred, 0.0, np.nan), "x_he": m.x_he,
        "x_co2_inferred": inferred, "d0_mm": m.d0_mm, "fiber": m.fiber.astype("boolean"), "test_end": None,
        "d_ext_hot_mm": m.d_ext_hot_mm, "d_ext_cool_mm": m.d_ext_cool_mm, "k_hot_mm2_s": m.k_hot_mm2_s,
        "flex_burning_rate_unverified": np.nan, "k_cool_mm2_s": m.k_cool_mm2_s,
        "burn_time_s": m.hf_burn_time, "reignitions": m.reignitions.astype("Int64"),
        "analysis_complete": m.analysis_complete.astype("boolean"),
        "quality_flags": np.where(~inferred, "O2+N2+He != 1 (x_co2 left NULL)", None),
        "source_file": m.source_file, "source_row": m.source_row,
    })
    checks["cfi_x_co2_inferred_zero"] = f"{int(inferred.sum())}/{len(c)}"
    d = pd.concat([f, c], ignore_index=True)
    for col in ("fiber", "analysis_complete"):
        d[col] = d[col].astype("boolean")
    d["reignitions"] = d["reignitions"].astype("Int64")
    d["test_id"] = d["test_id"].astype(str)
    return d, checks


# ============================================================================ droplet_reference_points
def build_droplet_reference_points() -> tuple[pd.DataFrame, dict[str, Any]]:
    pts, readme = _silver("psi117__figure_points"), _silver("psi117__readme")
    rd = readme.drop_duplicates("data_file").set_index("data_file")
    cols = ["fuel", "d0_mm_raw", "p_atm_raw", "xo2_raw", "xn2_raw", "third_component", "third_component_raw", "doi", "figure"]
    out = pts.join(rd[cols], on="data_file")
    missing = sorted(set(pts.data_file) - set(rd.index))
    return out, {"files_without_readme_conditions": missing, "points_by_role": out.role.value_counts().to_dict()}


# ============================================================================ investigations + publications
def hardware_family(hw: Any, project_type: Any) -> str:
    s = str(hw or "").lower()
    if "saffire" in s or "cygnus" in s:
        return "Saffire (Cygnus)"
    if "mdca" in s or "droplet combustion" in s:
        return "CIR-MDCA"
    if "acme" in s:
        return "CIR-ACME"
    if "glovebox" in s or "msg" in s:
        return "MSG"
    if "soot diagnostic" in s:
        return "CSD (SAME)"
    if "p-trak" in s:
        return "P-Trak (DAFT)"
    if "laboratory" in s or project_type == "Ground Investigation":
        return "Ground lab"
    return "unknown"


def build_investigations(gas: pd.DataFrame, drops: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    from flamesafe.ingestion import triage as tri

    inv = pd.read_parquet(config.data_dir() / "silver" / "catalog" / "investigations.parquet")
    t = tri.compute(config.load("triage"), inv)
    keep = ["psi_id", "R1", "R2", "R3", "R4", "R5", "R6", "score", "tier", "tier_notes", "pillars", "environments", "rqs",
            "justification"]
    out = inv.merge(t[keep], on="psi_id", how="left", validate="one_to_one")
    out["hardware_family"] = [hardware_family(h, p) for h, p in zip(out.experiment_hardware, out.project_type, strict=True)]
    counts = pd.concat([gas.groupby("psi_id").size(), drops.groupby("psi_id").size()]).groupby(level=0).sum()
    out["n_gold_tests"] = out.psi_id.map(counts).fillna(0).astype(int)
    mvp = {"PSI-159": "RQ1", "PSI-10": "RQ1", "PSI-69": "RQ2", "PSI-39": "RQ2", "PSI-117": "RQ2 (validation)"}
    out["mvp_role"] = out.psi_id.map(mvp)
    return out, {"hardware_family": out.hardware_family.value_counts().to_dict()}


def build_publications() -> tuple[pd.DataFrame, dict[str, Any]]:
    pubs = pd.read_parquet(config.data_dir() / "silver" / "catalog" / "publications.parquet")
    with_doi = pubs[pubs.doi.notna()]
    agg = (with_doi.groupby("doi")
           .agg(title=("title", "first"), author_list=("author_list", "first"), status=("status", "first"),
                psi_ids=("psi_id", lambda s: sorted(set(s), key=lambda x: int(x.split("-")[1]))))
           .reset_index())
    agg["n_records"] = agg.psi_ids.map(len)
    no_doi = pubs[pubs.doi.isna()][["doi", "title", "author_list", "status"]].copy()
    no_doi["psi_ids"] = pubs[pubs.doi.isna()].psi_id.map(lambda x: [x])
    no_doi["n_records"] = 1
    out = pd.concat([agg, no_doi], ignore_index=True)
    return out, {"silver_rows": len(pubs), "unique_doi": len(agg), "without_doi": len(no_doi),
                 "doi_shared_by_several_records": int((agg.n_records > 1).sum())}


# ============================================================================ invariants & runner
def invariants(gas: pd.DataFrame, drops: pd.DataFrame) -> list[dict[str, Any]]:
    rules = [
        ("gas_flame_tests", "xo2 in [0,1]", ~gas.xo2.dropna().between(0, 1)),
        ("gas_flame_tests", "x_fuel in [0,1]", ~gas.x_fuel.dropna().between(0, 1)),
        ("gas_flame_tests", "p_kpa > 0", ~gas.p_kpa.dropna().gt(0)),
        ("gas_flame_tests", "tad_k in (300, 3500)", ~gas.tad_k.dropna().between(300, 3500)),
        ("gas_flame_tests", "unique (psi_id, test_id)", gas.duplicated(["psi_id", "test_id"])),
        ("droplet_tests", "mole fractions in [0,1]",
         ~drops[["x_o2", "x_n2", "x_he"]].stack().between(0, 1)),
        ("droplet_tests", "sum of mole fractions <= 1.02",
         (drops[["x_o2", "x_n2", "x_co2", "x_he"]].sum(axis=1, min_count=1) > 1.02)),
        ("droplet_tests", "p_kpa > 0", ~drops.p_kpa.dropna().gt(0)),
        # small excess (< 5 %) is physically plausible (droplet thermal swelling during heat-up); larger is suspicious
        ("droplet_tests", "d_ext_hot <= 1.05 * d0 (when both present)",
         (drops.d_ext_hot_mm > 1.05 * drops.d0_mm)),
        ("droplet_tests", "unique (psi_id, test_id)", drops.duplicated(["psi_id", "test_id"])),
    ]
    return [{"table": t, "rule": r, "violations": int(mask.sum())} for t, r, mask in rules]


def run(out_dir: Path | None = None) -> dict[str, Any]:
    out_dir = out_dir or gold_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    gas, gchk = build_gas_flame_tests()
    drops, dchk = build_droplet_tests()
    refs, rchk = build_droplet_reference_points()
    inv, ichk = build_investigations(gas, drops)
    pubs, pchk = build_publications()
    tables = {"gas_flame_tests": gas, "droplet_tests": drops, "droplet_reference_points": refs,
              "investigations": inv, "publications": pubs}
    for name, df in tables.items():
        df.to_parquet(out_dir / f"{name}.parquet", index=False)
    _write_duckdb(out_dir, tables)
    inv_checks = invariants(gas, drops)
    report = {
        "built_at_utc": datetime.now().astimezone().isoformat(timespec="seconds"),
        "row_counts": {k: len(v) for k, v in tables.items()},
        "checks": {"gas_flame_tests": gchk, "droplet_tests": dchk, "droplet_reference_points": rchk,
                   "investigations": ichk, "publications": pchk},
        "outcome_coverage": {
            "gas_flame_tests_with_ignited": int(gas.ignited.notna().sum()),
            "droplet_tests_with_k_hot": int(drops.k_hot_mm2_s.notna().sum()),
            "droplet_tests_with_d_ext_hot": int(drops.d_ext_hot_mm.notna().sum()),
            "flex_with_test_end": int(drops.test_end.notna().sum()),
            "droplets_d_ext_hot_slightly_above_d0": int(((drops.d_ext_hot_mm > drops.d0_mm)
                                                         & (drops.d_ext_hot_mm <= 1.05 * drops.d0_mm)).sum()),
        },
        "invariants": inv_checks,
        "n_invariant_violations": sum(i["violations"] for i in inv_checks),
    }
    rep = out_dir / "_reports"
    rep.mkdir(exist_ok=True)
    with open(rep / "gold_report.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, default=str)
        fh.write("\n")
    report["out_dir"] = str(out_dir)
    return report


def _write_duckdb(out_dir: Path, tables: dict[str, pd.DataFrame]) -> None:
    import duckdb

    path = out_dir / "flamesafe.duckdb"
    con = duckdb.connect(str(path))
    try:
        for name in tables:
            pq = (out_dir / f"{name}.parquet").as_posix()
            con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_parquet('{pq}')")
    finally:
        con.close()
