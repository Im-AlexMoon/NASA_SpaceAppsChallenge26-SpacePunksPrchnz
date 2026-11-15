"""Right-censored accelerated-failure-time (AFT) regression by maximum likelihood, with a choice of error family.

    ln(T) = X @ beta + sigma * eps,   eps ~ extreme-value (Weibull), normal (lognormal) or logistic (log-logistic)

exp(beta_j) is a time ratio. A fast, dependency-light fitter (scipy only) so that leave-one-day-out validation and
day bootstraps of many candidate equations stay cheap. Log-likelihoods are on the ln(T) scale: comparable across
families and feature sets fitted to the same data, not with lifelines' (which works on the T scale).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import optimize
from scipy import stats as st

FAMILIES = ("weibull", "lognormal", "loglogistic")


def _loglik(theta: np.ndarray, x: np.ndarray, y: np.ndarray, event: np.ndarray, family: str) -> np.ndarray:
    sigma = np.exp(theta[-1])
    z = (y - x @ theta[:-1]) / sigma
    if family == "weibull":
        log_f, log_s = z - np.exp(z) - np.log(sigma), -np.exp(z)
    elif family == "lognormal":
        log_f, log_s = st.norm.logpdf(z) - np.log(sigma), st.norm.logsf(z)
    elif family == "loglogistic":
        log_f, log_s = z - 2 * np.logaddexp(0, z) - np.log(sigma), -np.logaddexp(0, z)
    else:
        raise ValueError(f"unknown family: {family}")
    return np.where(event == 1, log_f, log_s)


@dataclass
class AFTFit:
    columns: list[str]
    family: str
    theta: np.ndarray  # intercept, slopes..., log(sigma)
    log_likelihood: float

    @property
    def coef(self) -> pd.Series:
        return pd.Series(self.theta, index=["Intercept", *self.columns, "log_sigma"])

    @property
    def aic(self) -> float:
        return 2 * len(self.theta) - 2 * self.log_likelihood

    def predict_log_time(self, df: pd.DataFrame) -> np.ndarray:
        """Location of ln(T): the median of ln(T) for lognormal and log-logistic errors."""
        return design(df, self.columns) @ self.theta[:-1]

    def loglik(self, df: pd.DataFrame, duration: str = "duration_s", event: str = "event") -> np.ndarray:
        """Per-observation log-likelihood (density if the event was seen, survival if censored)."""
        return _loglik(self.theta, design(df, self.columns), np.log(df[duration].to_numpy(float)),
                       df[event].to_numpy(), self.family)

    def survival(self, df: pd.DataFrame, t: float) -> np.ndarray:
        """P(T > t) for each row."""
        z = (np.log(t) - self.predict_log_time(df)) / np.exp(self.theta[-1])
        if self.family == "weibull":
            return np.exp(-np.exp(z))
        return st.norm.sf(z) if self.family == "lognormal" else 1 / (1 + np.exp(z))


def design(df: pd.DataFrame, columns: list[str]) -> np.ndarray:
    return np.column_stack([np.ones(len(df)), df[columns].to_numpy(float)]) if columns else np.ones((len(df), 1))


def fit_aft(df: pd.DataFrame, columns: list[str], family: str = "loglogistic", duration: str = "duration_s",
            event: str = "event") -> AFTFit:
    """Fit ln(duration) ~ columns with right censoring (event == 0). Durations must be > 0 and inputs free of NaN."""
    x, y, e = design(df, columns), np.log(df[duration].to_numpy(float)), df[event].to_numpy()
    start = np.r_[np.linalg.lstsq(x, y, rcond=None)[0], 0.0]
    res = optimize.minimize(lambda th: -_loglik(th, x, y, e, family).sum(), start, method="BFGS")
    return AFTFit(list(columns), family, res.x, float(-res.fun))


def grouped_oof_loglik(df: pd.DataFrame, columns: list[str], family: str = "loglogistic", groups: str = "test_day",
                       **kw) -> tuple[np.ndarray, np.ndarray]:
    """Leave-one-group-out per-observation log-likelihood (a proper score) and predicted ln(T) location."""
    ll, loc = np.full(len(df), np.nan), np.full(len(df), np.nan)
    g = df[groups].to_numpy()
    for key in pd.unique(g):
        test = g == key
        model = fit_aft(df[~test], columns, family, **kw)
        ll[test], loc[test] = model.loglik(df[test], **kw), model.predict_log_time(df[test])
    return ll, loc


def bootstrap_coef(df: pd.DataFrame, columns: list[str], family: str = "loglogistic", groups: str = "test_day",
                   n_boot: int = 500, seed: int = 26, **kw) -> pd.DataFrame:
    """Point estimates with percentile 95% CIs from resampling whole groups (days) with replacement."""
    rng = np.random.default_rng(seed)
    g = df[groups].to_numpy()
    index = {k: np.flatnonzero(g == k) for k in pd.unique(g)}
    keys = list(index)
    draws = []
    for _ in range(n_boot):
        rows = np.concatenate([index[k] for k in rng.choice(keys, size=len(keys), replace=True)])
        draws.append(fit_aft(df.iloc[rows], columns, family, **kw).theta)
    lo, hi = np.quantile(np.array(draws), [0.025, 0.975], axis=0)
    return pd.DataFrame({"coef": fit_aft(df, columns, family, **kw).theta, "ci_low": lo, "ci_high": hi},
                        index=["Intercept", *columns, "log_sigma"])
