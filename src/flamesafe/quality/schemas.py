"""DE-09 · Data-quality contracts (pandera) for silver MVP tables and gold tables.

Contracts encode what DATA_DICTIONARY.md promises: types, physical ranges, allowed categories, keys, provenance.
They never "fix" data — a failure is reported with the offending values (flamesafe validate).
"""

from __future__ import annotations

import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

FRACTION = Check.in_range(0.0, 1.0)
POSITIVE = Check.gt(0)
NONNEG = Check.ge(0)

PROVENANCE = {
    "psi_id": Column(str, Check.str_matches(r"^PSI-\d+$")),
    "source_file": Column(str),
    "source_row": Column(int, Check.ge(2)),  # row 1 is always a header
}
SILVER_PROVENANCE = {**PROVENANCE, "source_sha256": Column(str, Check.str_matches(r"^[0-9a-f]{64}$"))}


def _frac(nullable: bool = True) -> Column:
    return Column(float, FRACTION, nullable=nullable)


def _num(*checks: Check, nullable: bool = True) -> Column:
    return Column(float, list(checks), nullable=nullable)


def _cat(values: list[str], nullable: bool = True) -> Column:
    return Column(str, Check.isin(values), nullable=nullable)


# ============================================================================ gold
GAS_FLAME_TESTS = DataFrameSchema(
    {
        **PROVENANCE,
        "campaign": _cat(["CFI-G", "Flame Design"], nullable=False),
        "test_id": Column(str, Check.str_matches(r"^\S+$")),
        "test_day": Column(int, NONNEG),
        "flame_type": _cat(["normal", "inverse"], nullable=False),
        "fuel": _cat(["ethylene", "ethane", "propane", "butane", "methane"], nullable=False),
        "fuel_dilution_pct": _num(Check.in_range(0, 100)),
        "xo2": _frac(), "xo2_final": _frac(), "x_fuel": _frac(),
        "p_kpa": _num(POSITIVE, Check.lt(1000), nullable=False),
        "p_source": _cat(["approx p (bar)", "pmean (atm)", "pinit (atm)"], nullable=False),
        "po2_kpa": _num(NONNEG),
        "m_fuel_mg_s": _num(NONNEG), "hc_burnrate_mg_s": _num(NONNEG), "m_o2_mg_s": _num(NONNEG),
        "m_n2_mg_s": _num(NONNEG), "m_total_mg_s": _num(NONNEG),
        "zst": _frac(), "tad_k": _num(Check.in_range(300, 3500)),
        "ignited": Column("boolean", nullable=True),
        "ignition_outcome": _cat(["yes", "no", "flash"]),
        "outcome_source": _cat(["experimental_table", "eventdata", "none"], nullable=False),
        "ignite_eventdata": Column("boolean", nullable=True),
        "extinction_mode": _cat(["self_extinguished", "flow_terminated"]),
        "burn_time_s": _num(NONNEG),
        "cool_flame": Column("boolean", nullable=True),
        "peak_burner_t_k": _num(Check.in_range(200, 1500)),
        "tfp": Column("boolean", nullable=True),
        "qualifier": _cat(["RAMP", "RAMPED", "LOW O2"]),
    },
    checks=[
        Check(lambda df: ~df.duplicated(["psi_id", "test_id"]), name="unique (psi_id, test_id)"),
        Check(lambda df: df["ignited"].isna() | df["ignition_outcome"].isin(["yes", "no"]),
              name="ignited only set from yes/no outcomes (flash stays NULL)"),
        Check(lambda df: (df["outcome_source"] != "none") | df["ignition_outcome"].isna(),
              name="outcome_source=none implies no outcome"),
        Check(lambda df: (df["po2_kpa"] - df["xo2"] * df["p_kpa"]).abs().fillna(0) < 1e-9, name="po2 = xo2 * p"),
    ],
    strict=True, coerce=False, name="gold.gas_flame_tests",
)

DROPLET_TESTS = DataFrameSchema(
    {
        **PROVENANCE,
        "campaign": _cat(["FLEX", "CFI"], nullable=False),
        "test_id": Column(str),
        "test_date": Column("datetime64[us]", nullable=True),
        "fuel": Column(str),
        "fuel_blend": Column(str, Check.str_matches(r"^\d+/\d+$"), nullable=True),
        "p_kpa": _num(POSITIVE, Check.lt(1000)),
        "x_o2": _frac(False), "x_n2": _frac(False), "x_co2": _frac(), "x_he": _frac(False),
        "x_co2_inferred": Column(bool),
        "d0_mm": _num(POSITIVE, Check.lt(20)),
        "fiber": Column("boolean", nullable=True),
        "test_end": _cat(["extinction", "disruption", "completion"]),
        "d_ext_hot_mm": _num(NONNEG, Check.lt(20)), "d_ext_cool_mm": _num(NONNEG, Check.lt(20)),
        "k_hot_mm2_s": _num(NONNEG, Check.lt(5)), "k_cool_mm2_s": _num(NONNEG, Check.lt(5)),
        "flex_burning_rate_unverified": _num(NONNEG),
        "burn_time_s": _num(NONNEG),
        "reignitions": Column("Int64", NONNEG, nullable=True),
        "analysis_complete": Column("boolean", nullable=True),
        "quality_flags": Column(str, nullable=True),
    },
    checks=[
        Check(lambda df: ~df.duplicated(["psi_id", "test_id"]), name="unique (psi_id, test_id)"),
        Check(lambda df: df[["x_o2", "x_n2", "x_co2", "x_he"]].sum(axis=1, min_count=1) <= 1.02,
              name="sum of mole fractions <= 1.02"),
        Check(lambda df: (df["campaign"] != "FLEX") | df["k_hot_mm2_s"].isna(),
              name="FLEX burning rate not promoted to k_hot (R-DE-05b)"),
        Check(lambda df: ~df["x_co2_inferred"] | (df["x_co2"] == 0), name="x_co2_inferred implies x_co2 = 0"),
    ],
    strict=True, coerce=False, name="gold.droplet_tests",
)

DROPLET_REFERENCE_POINTS = DataFrameSchema(
    {
        "psi_id": Column(str, Check.eq("PSI-117")),
        "data_file": Column(str), "block": Column(int, POSITIVE),
        "role": _cat(["experiment", "model", "error_bar", "unknown"], nullable=False),
        "x_name": Column(str), "x": Column(float), "y_name": Column(str), "y": Column(float),
        "source_row": Column(int, Check.ge(2)), "source_file": Column(str),
        "doi": Column(str, Check.str_matches(r"^10\.\d{4,9}/\S+$"), nullable=True),
    },
    strict=False, name="gold.droplet_reference_points",
)

INVESTIGATIONS = DataFrameSchema(
    {
        "psi_id": Column(str, Check.str_matches(r"^PSI-\d+$"), unique=True),
        "tier": Column(int, Check.isin([1, 2, 3])),
        "score": Column(float, Check.in_range(0, 1)),
        **{f"R{i}": Column(int, Check.in_range(0, 3)) for i in range(1, 7)},
        "access_status": _cat(["available", "experimental_table_only", "no_public_files"], nullable=False),
        "hardware_family": Column(str),
        "n_gold_tests": Column(int, NONNEG),
    },
    checks=[Check(lambda df: len(df) == 24, element_wise=False, name="24 combustion investigations")],
    strict=False, name="gold.investigations",
)

PUBLICATIONS = DataFrameSchema(
    {
        "doi": Column(str, Check.str_matches(r"^10\.\d{4,9}/\S+$"), nullable=True),
        "title": Column(str, nullable=True),
        "n_records": Column(int, POSITIVE),
    },
    checks=[Check(lambda df: ~df["doi"].dropna().duplicated().any(), element_wise=False, name="DOI unique")],
    strict=False, name="gold.publications",
)

GOLD = {
    "gas_flame_tests": GAS_FLAME_TESTS,
    "droplet_tests": DROPLET_TESTS,
    "droplet_reference_points": DROPLET_REFERENCE_POINTS,
    "investigations": INVESTIGATIONS,
    "publications": PUBLICATIONS,
}

# ============================================================================ silver (MVP semantic tables)
SILVER = {
    "psi159__normal_flames": DataFrameSchema({**SILVER_PROVENANCE, "test_id": Column(str, unique=True),
                                              "xo2_before": _frac(False), "ignition_outcome": _cat(["yes", "no", "flash"])},
                                             strict=False, name="silver.psi159__normal_flames"),
    "psi159__inverse_flames": DataFrameSchema({**SILVER_PROVENANCE, "test_id": Column(str, unique=True),
                                               "xo2": _frac(False), "ignition_outcome": _cat(["yes", "no", "flash"])},
                                              strict=False, name="silver.psi159__inverse_flames"),
    "psi10__normal_flames": DataFrameSchema({**SILVER_PROVENANCE, "test_id": Column(str, unique=True),
                                             "xo2_init": _frac(False), "p_init_atm": _num(POSITIVE, nullable=False)},
                                            strict=False, name="silver.psi10__normal_flames"),
    "psi10__inverse_flames": DataFrameSchema({**SILVER_PROVENANCE, "test_id": Column(str, unique=True),
                                              "xo2": _frac(), "p_init_atm": _num(POSITIVE, nullable=False)},
                                             strict=False, name="silver.psi10__inverse_flames"),
    "psi10__eventdata": DataFrameSchema({**SILVER_PROVENANCE, "op": Column(str, nullable=True),
                                         "ignite": Column(nullable=True)}, strict=False, name="silver.psi10__eventdata"),
    "psi159__eventdata": DataFrameSchema({**SILVER_PROVENANCE, "op": Column(str, nullable=True)},
                                         strict=False, name="silver.psi159__eventdata"),
    "psi69__flex_droplets": DataFrameSchema({**SILVER_PROVENANCE, "test_id": Column(str, unique=True),
                                             "x_o2": _frac(False), "x_co2": _frac(False), "x_he": _frac(False),
                                             "p_ambient_mmhg": _num(NONNEG, nullable=False),
                                             "test_end": _cat(["extinction", "disruption", "completion"], nullable=False)},
                                            strict=False, name="silver.psi69__flex_droplets"),
    "psi39__cfi_tests": DataFrameSchema({**SILVER_PROVENANCE, "flex_number": Column(str, unique=True),
                                         "p_atm": _num(POSITIVE, nullable=False), "x_o2": _frac(False)},
                                        strict=False, name="silver.psi39__cfi_tests"),
    "psi39__cfi_results": DataFrameSchema({**SILVER_PROVENANCE, "flex_number": Column(str, unique=True),
                                           "k_hot_mm2_s": _num(NONNEG)}, strict=False, name="silver.psi39__cfi_results"),
    "psi117__figure_points": DataFrameSchema({"psi_id": Column(str), "source_sha256": Column(str),
                                              "role": _cat(["experiment", "model", "error_bar", "unknown"], nullable=False)},
                                             strict=False, name="silver.psi117__figure_points"),
}
GENERIC_ET = DataFrameSchema(SILVER_PROVENANCE, strict=False, name="silver.et__*")

__all__ = ["GOLD", "SILVER", "GENERIC_ET", "pa"]
