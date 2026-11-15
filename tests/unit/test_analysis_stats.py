"""DS-05: statistical helpers on synthetic data with a known answer."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("statsmodels")

from flamesafe.analysis import stats  # noqa: E402


@pytest.fixture
def synthetic():
    rng = np.random.default_rng(0)
    n = 600
    x = rng.uniform(0.1, 0.5, n)
    day = rng.integers(0, 12, n)
    p = 1 / (1 + np.exp(-(-6 + 20 * x)))  # P = 0.5 at x = 0.3
    return pd.DataFrame({"x": x, "test_day": day, "y": (rng.uniform(size=n) < p).astype(float)})


def test_holm_matches_definition():
    adj = stats.holm([0.01, 0.04, 0.03, 0.5])
    assert np.allclose(adj, [0.04, 0.09, 0.09, 0.5])


def test_fit_logit_recovers_slope_and_threshold(synthetic):
    fit = stats.fit_logit(synthetic, "y ~ x")
    assert fit.n == 600 and fit.n_groups == 12
    assert 14 < fit.result.params["x"] < 26
    assert stats.logit_threshold(fit.result, 0.5, "x", {}) == pytest.approx(0.3, abs=0.03)
    orr = fit.odds_ratios({"x": 0.05}).iloc[0]
    assert orr.ci_low < orr.odds_ratio < orr.ci_high and orr.p_value < 1e-6


def test_grouped_cv_prefers_true_model(synthetic):
    good = stats.grouped_cv_logloss(synthetic, "y ~ x", "y")
    null = stats.grouped_cv_logloss(synthetic, "y ~ 1", "y")
    assert good["log_loss"] < null["log_loss"] and good["n_scored"] == 600 and good["folds_skipped"] == 0


def test_cluster_bootstrap_ci_contains_estimate(synthetic):
    out = stats.cluster_bootstrap(synthetic, lambda d: d.y.mean(), n_boot=200)
    assert out["ci_low"] <= out["estimate"] <= out["ci_high"] and out["n_ok"] == 200
