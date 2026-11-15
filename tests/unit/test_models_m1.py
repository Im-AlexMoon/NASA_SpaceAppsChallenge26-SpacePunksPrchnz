"""M1: cohorts, validation helpers and survival model on synthetic data with a known answer."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from flamesafe.models import m1


def _gas(rows):
    base = {"campaign": "CFI-G", "flame_type": "normal", "p_kpa": 101.3, "x_fuel": 0.3, "m_fuel_mg_s": 1.0,
            "m_o2_mg_s": np.nan, "xo2": 0.21, "test_day": 1, "burn_time_s": 10.0, "extinction_mode": "self_extinguished"}
    return pd.DataFrame([{**base, **r} for r in rows])


def test_cohorts_apply_exclusions_and_flash_policy():
    gas = _gas([
        {"test_id": "A1", "ignition_outcome": "yes"},
        {"test_id": "A2", "ignition_outcome": "no", "burn_time_s": 0.0, "extinction_mode": None},
        {"test_id": "A3", "ignition_outcome": "flash", "burn_time_s": 1.0},
        {"test_id": "A4", "ignition_outcome": "yes", "x_fuel": 0.0},          # zero-fuel control
        {"test_id": "21265H1", "ignition_outcome": "yes"},                    # audit anomaly
        {"test_id": "A5", "ignition_outcome": "yes", "campaign": "Flame Design"},
        {"test_id": "A6", "ignition_outcome": "yes", "extinction_mode": "flow_terminated", "burn_time_s": 66.0},
    ])
    ign = m1.ignition_cohort(gas)
    assert sorted(ign.test_id) == ["A1", "A2", "A6"] and ign.set_index("test_id").y.to_dict() == {"A1": 1, "A2": 0, "A6": 1}
    assert m1.ignition_cohort(gas, flash_as="no").set_index("test_id").y["A3"] == 0
    surv = m1.survival_cohort(gas)
    assert sorted(surv.test_id) == ["A1", "A6"] and surv.set_index("test_id").event.to_dict() == {"A1": 1, "A6": 0}
    assert "A3" in set(m1.survival_cohort(gas, include_flash=True).test_id)


def test_binary_metrics_known_values():
    out = m1.binary_metrics(np.array([0, 0, 1, 1]), np.array([0.1, 0.4, 0.35, 0.8]))
    assert out["auc"] == pytest.approx(0.75) and out["brier"] == pytest.approx((0.01 + 0.16 + 0.4225 + 0.04) / 4)


def test_grouped_oof_holds_out_whole_groups():
    df = pd.DataFrame({"test_day": [1, 1, 2, 2, 3], "v": [1.0, 2.0, 3.0, 4.0, 5.0]})
    seen = []

    def fp(train, test):
        seen.append(set(train.test_day) & set(test.test_day))
        return np.full(len(test), train.v.mean())

    oof, skipped = m1.grouped_oof(df, fp)
    assert skipped == 0 and all(not s for s in seen) and oof.notna().all()
    assert oof.iloc[4] == pytest.approx(2.5)


def test_nested_ignition_learns_lean_limit():
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(3)
    n = 240
    d = pd.DataFrame({"xo2": rng.uniform(0.15, 0.5, n), "log_p": np.log(rng.uniform(50, 300, n)),
                      "log_xfuel": np.log(rng.uniform(0.01, 1.0, n)), "fuel": rng.choice(["a", "b"], n),
                      "test_day": rng.integers(0, 8, n)})
    d["y"] = (rng.uniform(size=n) < np.where(d.log_xfuel < np.log(0.05), 0.05, 0.9)).astype(float)
    oof, skipped = m1.grouped_oof(d, m1.nested_ignition_fp())
    base, _ = m1.grouped_oof(d, lambda tr, te: np.full(len(te), tr.y.mean()))
    assert skipped == 0 and m1.binary_metrics(d.y, oof)["log_loss"] < m1.binary_metrics(d.y, base)["log_loss"]


def test_domain_status_requires_tests_and_days():
    df = pd.DataFrame({"xo2": [0.21, 0.22, 0.20, 0.21, 0.23, 0.50], "p_kpa": [100, 101, 99, 102, 100, 100],
                       "test_day": [1, 1, 2, 2, 2, 3]})
    assert m1.domain_status(df, 0.21, 100)["in_domain"]
    assert not m1.domain_status(df, 0.30, 70)["in_domain"]
    assert not m1.domain_status(df.assign(test_day=1), 0.21, 100)["in_domain"]  # one day only


@pytest.fixture
def weibull_data():
    rng = np.random.default_rng(1)
    n = 400
    x = rng.uniform(0.15, 0.85, n)
    scale = np.exp(2.0 + 2.0 * x)  # true time ratio per +0.05 = exp(0.1)
    t = scale * rng.weibull(1.5, n)
    cut = rng.uniform(5, 120, n)
    return pd.DataFrame({"xo2": x, "duration_s": np.minimum(t, cut), "event": (t <= cut).astype(int),
                         "test_day": rng.integers(0, 10, n)})


def test_weibull_aft_recovers_time_ratio_and_ranks(weibull_data):
    pytest.importorskip("lifelines")
    model = m1.fit_weibull_aft(weibull_data, "xo2")
    tr = m1.time_ratios(model, {"xo2": 0.05}).iloc[0]
    assert tr.ci_low < np.exp(0.1) < tr.ci_high
    c = m1.concordance(weibull_data.duration_s, model.predict_median(weibull_data), weibull_data.event)
    assert c > 0.6
    boot = m1.time_ratios_bootstrap(weibull_data, "xo2", {"xo2": 0.05}, n_boot=60).iloc[0]
    assert boot.boot_ci_low < np.exp(0.1) < boot.boot_ci_high and boot.n_boot_ok == 60


def test_bootstrap_predict_interval_brackets_point(weibull_data):
    pytest.importorskip("lifelines")
    scen = pd.DataFrame({"xo2": [0.2, 0.8]})
    out = m1.bootstrap_predict(weibull_data, lambda tr, te: m1.fit_weibull_aft(tr, "xo2").predict_median(te),
                               scen, n_boot=40)
    assert (out.lo <= out.pred).all() and (out.pred <= out.hi).all() and out.pred.iloc[1] > out.pred.iloc[0]


def test_cox_clustered_gives_protective_hazard_ratio(weibull_data):
    pytest.importorskip("lifelines")
    s = m1.fit_cox(weibull_data, "xo2").summary.loc["xo2"]
    assert s["exp(coef)"] < 1 and s["p"] < 0.01  # longer-lived flames -> lower hazard of self-extinction
