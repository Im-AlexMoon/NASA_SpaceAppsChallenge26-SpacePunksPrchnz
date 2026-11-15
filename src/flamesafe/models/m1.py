"""M1 · Ignition probability and burn duration of CFI-G gas jet flames.

Two targets, both from `gas_flame_tests` restricted to CFI-G (Flame Design labels are ~always "yes" and come from an
operational decision, so they cannot teach the model when a flame does *not* ignite):

* **Ignition** (binary): `ignited` for tests with a known label. `flash` is kept out of the binary target and handled
  as a sensitivity analysis (PHY decision 2026-11-14).
* **Burn duration** (survival): time from ignition to the end of the flame. A self-extinguished flame is an *event*;
  a flame still burning when the fuel/oxidizer flow was cut (`flow_terminated`) is *right-censored* at that time.

Normal and inverse flames swap the roles of burner stream and chamber atmosphere, so every model is fit per flame type.
Tests from the same operations day are not independent: inference is cluster-robust by `test_day` and validation is
leave-one-day-out. None of this is partial-gravity evidence: PSI data are microgravity only.
"""

from __future__ import annotations

import re
from collections.abc import Callable

import numpy as np
import pandas as pd

GROUP = "test_day"
# Chronology anomaly found by the team audit (end ~1 day before start); excluded from the main cohort, as in PR #3.
AUDIT_EXCLUDED_TESTS = frozenset({"21265H1"})
FLOW = {"normal": "m_fuel_mg_s", "inverse": "m_o2_mg_s"}


def _base(gas: pd.DataFrame) -> pd.DataFrame:
    d = gas[gas["campaign"].eq("CFI-G")].copy()
    d = d[~d["test_id"].isin(AUDIT_EXCLUDED_TESTS)]
    d = d[d["x_fuel"].gt(0)]  # zero-fuel controls (21125A4, 21125H3) cannot ignite by construction
    d["log_p"] = np.log(d["p_kpa"])
    d["log_xfuel"] = np.log(d["x_fuel"])
    for ft, col in FLOW.items():
        m = d["flame_type"].eq(ft)
        d.loc[m, "log_flow"] = np.log(d.loc[m, col])
    return d


def ignition_cohort(gas: pd.DataFrame, flash_as: str | None = None) -> pd.DataFrame:
    """CFI-G tests with a binary ignition target `y`.

    flash_as=None drops the 8 `flash` tests (main analysis); "yes"/"no" recodes them for the sensitivity analysis.
    """
    d = _base(gas)
    outcome = d["ignition_outcome"]
    if flash_as is None:
        d = d[outcome.isin(["yes", "no"])]
    else:
        d = d[outcome.isin(["yes", "no", "flash"])]
        d = d.assign(ignition_outcome=d["ignition_outcome"].replace({"flash": flash_as}))
    return d.assign(y=d["ignition_outcome"].eq("yes").astype(float))


def survival_cohort(gas: pd.DataFrame, include_flash: bool = False) -> pd.DataFrame:
    """Ignited CFI-G flames with `duration_s` and `event` (1 = self-extinguished, 0 = censored by flow cut).

    include_flash=True adds the `flash` tests as immediate self-extinctions (sensitivity analysis).
    """
    d = _base(gas)
    keep = d["ignition_outcome"].eq("yes")
    if include_flash:
        keep |= d["ignition_outcome"].eq("flash")
    d = d[keep & d["extinction_mode"].notna() & d["burn_time_s"].gt(0)]
    return d.assign(duration_s=d["burn_time_s"].astype(float),
                    event=d["extinction_mode"].eq("self_extinguished").astype(int))


# --------------------------------------------------------------------------------------------------- validation

def grouped_oof(df: pd.DataFrame, fit_predict: Callable[[pd.DataFrame, pd.DataFrame], np.ndarray],
                groups: str = GROUP) -> tuple[pd.Series, int]:
    """Out-of-fold predictions holding out one whole group at a time. Folds that cannot fit are skipped and counted."""
    out = pd.Series(np.nan, index=df.index)
    skipped = 0
    for g in df[groups].unique():
        test = df[groups] == g
        try:
            out[test] = fit_predict(df[~test], df[test])
        except Exception:  # noqa: BLE001 - unseen category level, separation, non-convergence
            skipped += 1
    return out, skipped


def binary_metrics(y: np.ndarray, p: np.ndarray, eps: float = 1e-6) -> dict[str, float]:
    """Log-loss, Brier score and ROC-AUC (rank formulation, ties averaged)."""
    from scipy.stats import rankdata

    y, p = np.asarray(y, float), np.clip(np.asarray(p, float), eps, 1 - eps)
    pos, n_pos = y == 1, int((y == 1).sum())
    n_neg = len(y) - n_pos
    auc = ((rankdata(p)[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)) if n_pos and n_neg else np.nan
    return {"log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
            "brier": float(np.mean((p - y) ** 2)), "auc": float(auc)}


def concordance(duration: np.ndarray, predicted_time: np.ndarray, event: np.ndarray) -> float:
    """Harrell's C for right-censored data: higher predicted time should mean longer observed survival."""
    from lifelines.utils import concordance_index

    return float(concordance_index(duration, predicted_time, event))


# --------------------------------------------------------------------------------------------------- ignition

IGNITION_C_GRID = (0.1, 0.3, 1.0, 3.0, 10.0)


def ignition_pipeline(c: float, spline: bool = True, linear: tuple[str, ...] = ("xo2", "log_p")):
    """Penalized (L2) logistic regression: linear in O2 and log-pressure, cubic spline in log fuel fraction, fuel dummies.

    The spline captures the three fuel regimes found in RQ1 (lean limit, near-certain ignition, "no" cases returning at
    high fuel fraction). `extrapolation="constant"` keeps predictions flat outside the observed fuel-fraction range.
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler

    parts = [("lin", StandardScaler(), list(linear))]
    if spline:
        parts.append(("spl", SplineTransformer(n_knots=4, degree=3, extrapolation="constant"), ["log_xfuel"]))
    parts.append(("fuel", OneHotEncoder(handle_unknown="ignore"), ["fuel"]))
    return make_pipeline(ColumnTransformer(parts), LogisticRegression(C=c, max_iter=5000))


def select_c(train: pd.DataFrame, grid=IGNITION_C_GRID, groups: str = GROUP, **kw) -> float:
    """Pick the L2 strength by leave-one-group-out log-loss *inside* the training data (nested CV)."""
    scores = {}
    for c in grid:
        oof, _ = grouped_oof(train, lambda tr, te, c=c: ignition_pipeline(c, **kw).fit(tr, tr["y"]).predict_proba(te)[:, 1],
                             groups)
        ok = oof.notna()
        scores[c] = binary_metrics(train.loc[ok, "y"], oof[ok])["log_loss"] if ok.any() else np.inf
    return min(scores, key=scores.get)


def nested_ignition_fp(groups: str = GROUP, **kw) -> Callable[[pd.DataFrame, pd.DataFrame], np.ndarray]:
    """fit_predict for `grouped_oof` that re-selects C within each outer training fold."""
    def fp(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
        c = select_c(train, groups=groups, **kw)
        return ignition_pipeline(c, **kw).fit(train, train["y"]).predict_proba(test)[:, 1]
    return fp


# --------------------------------------------------------------------------------------------------- survival

def _model_frame(df: pd.DataFrame, formula: str, extra: list[str]) -> pd.DataFrame:
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", formula))
    cols = ["duration_s", "event", *extra]
    return df[cols + [c for c in df.columns if c in tokens and c not in cols]]


def fit_weibull_aft(df: pd.DataFrame, formula: str):
    """Weibull accelerated-failure-time model (used for predicted medians and survival curves).

    exp(coef) of a covariate in the `lambda_` block is a *time ratio*: >1 means flames last longer. lifelines has no
    clustered covariance for parametric models, so its CIs assume independent tests: use `time_ratios_bootstrap`
    (resampling whole days) for inference, or the Cox model with clustered errors.
    """
    from lifelines import WeibullAFTFitter

    return WeibullAFTFitter().fit(_model_frame(df, formula, []), duration_col="duration_s", event_col="event",
                                  formula=formula)


def fit_cox(df: pd.DataFrame, formula: str, groups: str = GROUP):
    """Cox proportional-hazards model with cluster-robust (sandwich) covariance by `groups`.

    exp(coef) is a hazard ratio of self-extinction: <1 means flames last longer.
    """
    from lifelines import CoxPHFitter

    return CoxPHFitter().fit(_model_frame(df, formula, [groups]), duration_col="duration_s", event_col="event",
                             formula=formula, cluster_col=groups)


def hazard_ratios(model, scale: dict[str, float] | None = None) -> pd.DataFrame:
    """Cox hazard ratio of self-extinction per `scale[term]` units (default 1), cluster-robust 95% CI."""
    scale = scale or {}
    rows = []
    for term, r in model.summary.iterrows():
        k = scale.get(term, 1.0)
        rows.append({"term": term, "per": k, "hazard_ratio": np.exp(r["coef"] * k),
                     "ci_low": np.exp(r["coef lower 95%"] * k), "ci_high": np.exp(r["coef upper 95%"] * k),
                     "p_value": r["p"]})
    return pd.DataFrame(rows)


def time_ratios(model, scale: dict[str, float] | None = None) -> pd.DataFrame:
    """Time ratio per `scale[term]` units of each covariate (default 1), with the model's (unclustered) 95% CI."""
    scale = scale or {}
    s = model.summary.loc["lambda_"]
    rows = []
    for term, r in s.iterrows():
        if term == "Intercept":
            continue
        k = scale.get(term, 1.0)
        rows.append({"term": term, "per": k, "time_ratio": np.exp(r["coef"] * k),
                     "ci_low": np.exp(r["coef lower 95%"] * k), "ci_high": np.exp(r["coef upper 95%"] * k),
                     "p_value": r["p"]})
    return pd.DataFrame(rows)


def time_ratios_bootstrap(df: pd.DataFrame, formula: str, scale: dict[str, float] | None = None,
                          groups: str = GROUP, n_boot: int = 300, seed: int = 26) -> pd.DataFrame:
    """Weibull AFT time ratios with percentile 95% CIs from resampling whole `groups` (days) with replacement."""
    import warnings

    point = time_ratios(fit_weibull_aft(df, formula), scale).set_index("term")
    rng = np.random.default_rng(seed)
    keys = df[groups].unique()
    by = {k: df[df[groups] == k] for k in keys}
    draws = []
    for _ in range(n_boot):
        sample = pd.concat([by[k] for k in rng.choice(keys, size=len(keys), replace=True)], ignore_index=True)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                draws.append(time_ratios(fit_weibull_aft(sample, formula), scale).set_index("term")["time_ratio"])
        except Exception:  # noqa: BLE001 - degenerate resample (e.g. a fuel level missing)
            continue
    b = pd.DataFrame(draws)
    point["boot_ci_low"] = b.quantile(0.025).reindex(point.index)
    point["boot_ci_high"] = b.quantile(0.975).reindex(point.index)
    point["n_boot_ok"] = len(b)
    return point.reset_index()


def bootstrap_predict(df: pd.DataFrame, fit_predict: Callable[[pd.DataFrame, pd.DataFrame], np.ndarray],
                      scenarios: pd.DataFrame, groups: str = GROUP, n_boot: int = 300, seed: int = 26,
                      level: float = 0.90) -> pd.DataFrame:
    """Point prediction for each scenario row plus a percentile interval from refitting on whole-day resamples."""
    import warnings

    rng = np.random.default_rng(seed)
    keys = df[groups].unique()
    by = {k: df[df[groups] == k] for k in keys}
    draws = []
    for _ in range(n_boot):
        sample = pd.concat([by[k] for k in rng.choice(keys, size=len(keys), replace=True)], ignore_index=True)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                draws.append(np.asarray(fit_predict(sample, scenarios), float))
        except Exception:  # noqa: BLE001 - degenerate resample
            continue
    b = np.vstack(draws)
    a = (1 - level) / 2
    return scenarios.assign(pred=np.asarray(fit_predict(df, scenarios), float), lo=np.quantile(b, a, axis=0),
                            hi=np.quantile(b, 1 - a, axis=0), n_boot_ok=len(draws))


# --------------------------------------------------------------------------------------------------- domain

def nearby_tests(df: pd.DataFrame, xo2: float, p_kpa: float, dxo2: float = 0.05, rel_p: float = 0.25) -> pd.DataFrame:
    """Tests within ±dxo2 (absolute mole fraction) and ±rel_p (relative) of a target atmosphere."""
    m = df["xo2"].sub(xo2).abs().le(dxo2) & df["p_kpa"].sub(p_kpa).abs().le(rel_p * p_kpa)
    return df[m]


def domain_status(df: pd.DataFrame, xo2: float, p_kpa: float, min_tests: int = 5, min_groups: int = 2,
                  groups: str = GROUP) -> dict[str, object]:
    """Applicability-domain verdict: a prediction is shown only if enough real tests from >1 day are nearby."""
    near = nearby_tests(df, xo2, p_kpa)
    n, k = len(near), int(near[groups].nunique()) if len(near) else 0
    return {"n_nearby": n, "days_nearby": k, "in_domain": bool(n >= min_tests and k >= min_groups)}
