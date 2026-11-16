"""M-01 v2 readings (ADR-0007): evidence tiers, withheld values, physical signs (PHY-04) and the committed artifact."""

from __future__ import annotations

import pandas as pd
import pytest

pytest.importorskip("cantera")

from flamesafe.models import readings  # noqa: E402


@pytest.fixture(scope="module")
def art():
    return readings.load()


def _gas(n, xo2, p, days):
    return pd.DataFrame([{"campaign": "CFI-G", "flame_type": "normal", "x_fuel": 0.3, "xo2": xo2, "p_kpa": p,
                          "test_id": f"T{i}", "test_day": days[i % len(days)], "fuel": "propane",
                          "ignition_outcome": "yes" if i % 3 else "no", "burn_time_s": 10.0 + i,
                          "extinction_mode": "self_extinguished"} for i in range(n)])


def test_committed_artifact_is_complete_and_signed(art):
    assert art["model_id"] == readings.MODEL_ID and art["features"] == readings.FEATURES
    assert len(art["bootstrap_draws"]) >= 200 and len(art["theta"]) == len(readings.FEATURES) + 2
    assert art["cohort"]["n"] > 200 and art["metrics"]["validation"] == "leave-one-operations-day-out"
    assert art["review"]["status"] == "reviewed" and art["review"]["phy_reviewer"]


def test_tiers(art):
    a = readings.read(art, 0.21, 101.3, _gas(8, 0.21, 101.3, [1, 2]))
    assert a["tier"] == "A" and a["prediction"]["median_burn_s"] > 0 and a["nearby"]["n_tests"] == 8
    b = readings.read(art, 0.30, 70.3, _gas(8, 0.21, 101.3, [1, 2]))
    assert b["tier"] == "B" and b["nearby"]["n_tests"] == 0 and "no tests" in b["caveats"][0]
    lo, hi = b["prediction"]["median_burn_s_90ci"]
    assert lo < b["prediction"]["median_burn_s"] < hi
    one_day = readings.read(art, 0.21, 101.3, _gas(8, 0.21, 101.3, [1]))
    assert one_day["tier"] == "B" and one_day["coverage"] == "limited"
    outside = readings.read(art, 0.21, 101.3, _gas(8, 0.21, 101.3, [1, 2]), m_fuel_mg_s=100)
    assert outside["coverage"] == "sufficient" and outside["prediction"] is None


def test_no_evidence_withholds_numbers(art):
    suit = readings.read(art, 1.0, 29.6)
    assert suit["tier"] == "C" and suit["prediction"] is None
    fuel = readings.read(art, 0.21, 101.3, fuel="ethylene")
    assert fuel["tier"] == "C" and fuel["prediction"] is None and "not tested" in fuel["reason"]


def test_partial_gravity_is_flagged_and_inputs_validated(art):
    moon = readings.read(art, 0.30, 70.3, gravity="moon")
    assert moon["gravity_effect"]["tier"] == "C" and moon["regime"] == "microgravity"
    with pytest.raises(ValueError):
        readings.read(art, 0.21, 101.3, gravity="venus")
    with pytest.raises(ValueError):
        readings.read(art, 1.5, 101.3)


def test_physical_signs_phy04(art):
    """More O2 -> longer-lived flame; more pressure -> shorter; more fuel flow -> shorter (RESEARCH_LOG R13)."""
    def median(**kw):
        base = {"xo2": 0.30, "p_kpa": 101.3, "fuel": "propane", "x_fuel": 0.3, "m_fuel_mg_s": 1.0}
        x = readings.source_features(**{**base, **kw})
        return float(readings._predict(pd.Series(art["theta"]).to_numpy(), pd.Series(x)[readings.FEATURES].to_numpy()))
    assert median(xo2=0.36) > median(xo2=0.30)
    assert median(p_kpa=200) < median(p_kpa=101.3)
    assert median(m_fuel_mg_s=2.0) < median(m_fuel_mg_s=1.0)
