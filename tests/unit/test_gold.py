"""DE-08: gold helpers (offline) + end-to-end build on the real silver layer (integration)."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from flamesafe.physics import units
from flamesafe.pipeline import gold


@pytest.mark.parametrize(("raw", "expected"), [
    ("30% butane", ("butane", 30.0)), ("C2H4", ("ethylene", 100.0)), ("c3h8", ("propane", 100.0)),
    ("Heptane", ("heptane", 100.0)), ("50 % ethane", ("ethane", 50.0)), (None, (None, None)),
    ("Exotic fuel", ("exotic fuel", 100.0)),
])
def test_parse_fuel(raw, expected):
    assert gold.parse_fuel(raw) == expected


@pytest.mark.parametrize(("hw", "ptype", "family"), [
    ("Saffire III enclosure in Cygnus", "Microgravity Investigation", "Saffire (Cygnus)"),
    ("Multi-user Droplet Combustion Appartatus (MDCA), CIR", "Microgravity Investigation", "CIR-MDCA"),
    ("ACME, Combustion Integrated Rack (CIR)", "Microgravity Investigation", "CIR-ACME"),
    ("Microgravity Science Glovebox", "Microgravity Investigation", "MSG"),
    ("Comparitive Soot Diagnostic Hardware", "Microgravity Investigation", "CSD (SAME)"),
    (None, "Ground Investigation", "Ground lab"),
    (None, "Microgravity Investigation", "unknown"),
])
def test_hardware_family(hw, ptype, family):
    assert gold.hardware_family(hw, ptype) == family


def test_qualifier_picks_ramp_tokens_only():
    df = pd.DataFrame({"x__flag": [None, "RAMP", "-"], "y__flag": ["LOW O2", None, "#DIV/0!"]})
    q = gold._qualifier(df)
    assert q.iloc[:2].tolist() == ["LOW O2", "RAMP"] and pd.isna(q.iloc[2])


def test_mmhg_conversion():
    assert math.isclose(units.mmhg_to_kpa(760), 101.325, rel_tol=1e-6)


def test_invariants_flag_violations():
    gas = pd.DataFrame({"psi_id": ["A", "A"], "test_id": ["1", "1"], "xo2": [0.2, 1.2], "x_fuel": [0.5, 0.5],
                        "p_kpa": [100, -1], "tad_k": [2000, 2000]})
    drops = pd.DataFrame({"psi_id": ["B"], "test_id": ["1"], "x_o2": [0.21], "x_n2": [0.79], "x_co2": [0.1],
                          "x_he": [0.0], "p_kpa": [101.3], "d0_mm": [2.0], "d_ext_hot_mm": [2.5]})
    v = {(i["table"], i["rule"]): i["violations"] for i in gold.invariants(gas, drops)}
    assert v[("gas_flame_tests", "xo2 in [0,1]")] == 1 and v[("gas_flame_tests", "p_kpa > 0")] == 1
    assert v[("gas_flame_tests", "unique (psi_id, test_id)")] == 1
    assert v[("droplet_tests", "sum of mole fractions <= 1.02")] == 1
    assert v[("droplet_tests", "d_ext_hot <= 1.05 * d0 (when both present)")] == 1


@pytest.mark.integration
def test_gold_build_on_real_silver(tmp_path):
    rep = gold.run(out_dir=tmp_path)
    rc = rep["row_counts"]
    assert rc["gas_flame_tests"] == 660 and rc["droplet_tests"] == 501 and rc["investigations"] == 24
    g = pd.read_parquet(tmp_path / "gas_flame_tests.parquet")
    assert g.groupby(["psi_id", "test_id"]).size().max() == 1
    assert set(g.outcome_source) <= {"experimental_table", "eventdata", "none"}
    assert g.loc[g.ignition_outcome == "flash", "ignited"].isna().all()       # flash is never forced to yes/no
    assert (g.loc[g.zst.notna() | g.tad_k.notna(), "campaign"].notna()).all()
    d = pd.read_parquet(tmp_path / "droplet_tests.parquet")
    assert d.loc[d.campaign == "FLEX", "k_hot_mm2_s"].isna().all()           # R-DE-05b: unverified unit stays out
    assert d.loc[d.p_kpa.notna(), "p_kpa"].gt(0).all()
    assert (tmp_path / "flamesafe.duckdb").exists()
