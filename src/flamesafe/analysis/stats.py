"""DS-05 · Statistical helpers for grouped (clustered) experimental data.

PSI tests are not independent: tests run on the same operations day share hardware state, crew procedures and
calibration. Every routine here therefore takes a `groups` column (normally `test_day`) and uses it for
cluster-robust standard errors, leave-one-group-out cross-validation and cluster bootstrap.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


@dataclass
class LogitFit:
    formula: str
    n: int
    n_groups: int
    aic: float
    result: object  # statsmodels GLMResults

    def odds_ratios(self, scale: dict[str, float] | None = None) -> pd.DataFrame:
        """Odds ratio per `scale[term]` units of each term (default 1), with 95% CI and p-value (cluster-robust)."""
        scale = scale or {}
        params, ci, p = self.result.params, self.result.conf_int(), self.result.pvalues
        rows = []
        for term in params.index:
            if term == "Intercept":
                continue
            k = scale.get(term, 1.0)
            rows.append({"term": term, "per": k, "odds_ratio": np.exp(params[term] * k),
                         "ci_low": np.exp(ci.loc[term, 0] * k), "ci_high": np.exp(ci.loc[term, 1] * k), "p_value": p[term]})
        return pd.DataFrame(rows)


def fit_logit(df: pd.DataFrame, formula: str, groups: str = "test_day") -> LogitFit:
    """Binomial GLM (logit) with cluster-robust covariance by `groups`. Rows with NaN in used columns must be removed first."""
    model = smf.glm(formula, df, family=sm.families.Binomial())
    res = model.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df[groups])[0]})
    return LogitFit(formula, int(res.nobs), int(df[groups].nunique()), float(res.aic), res)


def holm(pvalues: Sequence[float]) -> np.ndarray:
    """Holm-Bonferroni adjusted p-values (same order as input)."""
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adj[idx] = min(1.0, running)
    return adj


def log_loss(y: np.ndarray, p: np.ndarray, eps: float = 1e-12) -> float:
    p = np.clip(p, eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def grouped_cv_logloss(df: pd.DataFrame, formula: str, target: str, groups: str = "test_day") -> dict[str, float]:
    """Leave-one-group-out CV log-loss of a logit formula. Folds whose training set cannot fit are skipped and counted."""
    preds = pd.Series(np.nan, index=df.index)
    skipped = 0
    for g in df[groups].unique():
        train, test = df[df[groups] != g], df[df[groups] == g]
        try:
            res = smf.glm(formula, train, family=sm.families.Binomial()).fit()
            preds.loc[test.index] = res.predict(test)
        except Exception:  # noqa: BLE001 - e.g. unseen category level in the held-out day
            skipped += 1
    ok = preds.notna()
    return {"log_loss": log_loss(df.loc[ok, target].to_numpy(float), preds[ok].to_numpy()),
            "n_scored": int(ok.sum()), "folds_skipped": skipped}


def cluster_bootstrap(df: pd.DataFrame, stat: Callable[[pd.DataFrame], float], groups: str = "test_day",
                      n_boot: int = 500, seed: int = 26) -> dict[str, float]:
    """Percentile 95% CI of `stat` resampling whole groups with replacement. Failed resamples are dropped and counted."""
    rng = np.random.default_rng(seed)
    keys = df[groups].unique()
    by = {k: df[df[groups] == k] for k in keys}
    vals = []
    for _ in range(n_boot):
        sample = pd.concat([by[k] for k in rng.choice(keys, size=len(keys), replace=True)], ignore_index=True)
        try:
            with warnings.catch_warnings():  # separation in a resample floods numeric warnings; counted via n_failed/CI
                warnings.simplefilter("ignore")
                v = stat(sample)
        except Exception:  # noqa: BLE001 - perfect separation or degenerate resample
            continue
        if np.isfinite(v):
            vals.append(v)
    vals = np.asarray(vals)
    return {"estimate": float(stat(df)), "ci_low": float(np.percentile(vals, 2.5)) if len(vals) else np.nan,
            "ci_high": float(np.percentile(vals, 97.5)) if len(vals) else np.nan, "n_ok": int(len(vals)),
            "n_failed": int(n_boot - len(vals))}


def logit_threshold(res, target_p: float, solve_for: str, at: dict[str, float]) -> float:
    """Value of the linear term `solve_for` at which predicted probability equals `target_p`, holding `at` fixed.

    Works for formulas where `solve_for` enters linearly (no transforms). Categorical levels in `at` use patsy names,
    e.g. {"C(fuel)[T.ethane]": 1.0}. Returns NaN when the slope is ~0.
    """
    params = res.params
    eta_target = np.log(target_p / (1 - target_p))
    rest = params.get("Intercept", 0.0) + sum(params[k] * v for k, v in at.items() if k in params.index)
    slope = params[solve_for]
    return float((eta_target - rest) / slope) if abs(slope) > 1e-9 else float("nan")
