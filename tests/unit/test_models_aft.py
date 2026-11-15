"""AFT fitter and spherical-flame groups: synthetic data with a known answer."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from flamesafe.models import aft
from flamesafe.physics import spherical_flame as sf


@pytest.fixture
def censored():
    rng = np.random.default_rng(5)
    n = 500
    x = rng.uniform(0, 1, n)
    log_t = 1.0 + 2.0 * x + 0.5 * rng.logistic(size=n)  # log-logistic truth: slope 2, sigma 0.5
    cut = np.log(rng.uniform(2, 60, n))
    return pd.DataFrame({"x": x, "duration_s": np.exp(np.minimum(log_t, cut)), "event": (log_t <= cut).astype(int),
                         "test_day": rng.integers(0, 10, n)})


@pytest.mark.parametrize("family", aft.FAMILIES)
def test_fit_recovers_slope_under_censoring(censored, family):
    fit = aft.fit_aft(censored, ["x"], family)
    assert fit.coef["x"] == pytest.approx(2.0, abs=0.35)
    assert np.all(np.diff(fit.survival(censored.sort_values("x"), 10.0)) >= -1e-12)  # more x -> longer life


def test_true_family_and_covariate_win_out_of_fold(censored):
    ll_x, loc = aft.grouped_oof_loglik(censored, ["x"], "loglogistic")
    ll_null, _ = aft.grouped_oof_loglik(censored, [], "loglogistic")
    assert np.isfinite(ll_x).all() and ll_x.mean() > ll_null.mean()
    assert np.corrcoef(loc, np.log(censored.duration_s))[0, 1] > 0.5


def test_bootstrap_ci_covers_truth(censored):
    out = aft.bootstrap_coef(censored, ["x"], n_boot=80)
    assert out.loc["x", "ci_low"] < 2.0 < out.loc["x", "ci_high"]
    assert np.exp(out.loc["log_sigma", "coef"]) == pytest.approx(0.5, abs=0.1)


def test_spherical_groups_normal_and_inverse():
    df = pd.DataFrame({"flame_type": ["normal", "inverse", "normal"], "fuel": ["ethane", "butane", "propane"],
                       "x_fuel": [1.0, 0.1, 0.3], "xo2": [0.21, 1.0, 0.21], "m_fuel_mg_s": [2.0, np.nan, 1.0],
                       "m_o2_mg_s": [np.nan, 3.0, np.nan], "zst": [0.5, 0.5, np.nan]})
    out = sf.add_spherical_groups(df)
    assert out.y_burner.iloc[0] == pytest.approx(1.0) and out.m_tot_mg_s.iloc[0] == pytest.approx(2.0)
    assert out.y_burner.iloc[1] == pytest.approx(1.0) and out.m_tot_mg_s.iloc[1] == pytest.approx(3.0)
    assert out.log_term.iloc[0] == pytest.approx(np.log(2)) and out.log_term.iloc[1] == pytest.approx(np.log(2))
    assert out.r_ss_proxy.iloc[0] == pytest.approx(2.0 / np.log(2))
    expected_y = 0.3 * 44.096 / (0.3 * 44.096 + 0.7 * 28.013)
    assert out.y_burner.iloc[2] == pytest.approx(expected_y) and np.isnan(out.r_ss_proxy.iloc[2])  # NaN, never 0
