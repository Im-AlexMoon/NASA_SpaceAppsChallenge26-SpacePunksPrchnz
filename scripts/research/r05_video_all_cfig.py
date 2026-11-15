"""Research iteration 5 (2026-11-16): what the video of every CFI-G test adds (ADR-0009, phase 2).

1. Validation: flame duration from video vs the investigator's table and the time-series detector.
2. Flame-radius law: does the steady flame radius scale with m_tot / L (spherical-flame theory, slope 1 in log-log)?
3. Soot-glow precursor: does the yellow (soot) glow fade well before self-extinction, and not before a flow cut?
4. Shrinking before extinction.

Needs `flamesafe video-collect --source gs://flamesafe-psi-video/cfig-v2` (silver `acme__video_features`), gold and the
time-series features. Run: python scripts/research/r05_video_all_cfig.py
"""

from __future__ import annotations

import warnings

import duckdb
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from flamesafe import config
from flamesafe.analysis import stats
from flamesafe.physics.spherical_flame import add_spherical_groups

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)


def load() -> pd.DataFrame:
    con = duckdb.connect(str(config.data_dir() / "gold" / "flamesafe.duckdb"), read_only=True)
    gold = con.sql("SELECT * FROM gas_flame_tests WHERE campaign = 'CFI-G'").df()
    con.close()
    vid = pd.read_parquet(config.data_dir() / "silver" / "tables" / "acme__video_features.parquet")
    vid = vid.sort_values("bytes", ascending=False).drop_duplicates("test_id")  # one test has two recordings
    ts = pd.read_parquet(config.data_dir() / "silver" / "tables" / "acme__timeseries_features.parquet")
    ts = ts[ts.file_variant.isna()][["psi_id", "test_id", "flame_duration_s", "ts_extinction_mode", "ts_flame_class"]]
    d = gold.merge(vid.drop(columns=["psi_id", "source_file"]), on="test_id", how="inner").merge(ts, on=["psi_id", "test_id"], how="left")
    return add_spherical_groups(d)


def validate(d: pd.DataFrame) -> None:
    print("\n### 1. Duration: video vs investigator vs time series")
    print(f"videos matched to gold tests: {len(d)}; flame seen: {int(d.flame_seen.sum())}; "
          f"radius quality ok: {int(d.radius_quality.eq('ok').sum())}")
    print(pd.crosstab(d.ignition_outcome.fillna("NA"), d.flame_seen))
    s = d[d.flame_seen & d.burn_time_s.gt(0)]
    for ref in ("burn_time_s", "flame_duration_s"):
        x = s.dropna(subset=[ref])
        diff = x.flame_visible_s - x[ref]
        print(f"  vs {ref}: n={len(x)}, Spearman {x.flame_visible_s.corr(x[ref], method='spearman'):.3f}, "
              f"median diff {diff.median():+.2f} s, |diff| <= 2 s: {np.mean(diff.abs() <= 2):.2f}, <= 5 s: {np.mean(diff.abs() <= 5):.2f}")
    bad = s.assign(diff=s.flame_visible_s - s.burn_time_s).reindex((s.flame_visible_s - s.burn_time_s).abs().sort_values(ascending=False).index)
    print("  largest disagreements:")
    print(bad[["test_id", "flame_type", "burn_time_s", "flame_duration_s", "flame_visible_s", "radius_quality"]].head(8).to_string(index=False))


def radius_law(d: pd.DataFrame) -> None:
    print("\n### 2. Steady flame radius vs m_tot / L (theory: r proportional to m_tot / L, slope 1)")
    for ft, g in d[d.flame_seen & d.radius_quality.eq("ok") & d.ignition_outcome.eq("yes")].groupby("flame_type"):
        g = g.dropna(subset=["r_steady_px", "r_ss_proxy", "p_kpa"]).assign(
            log_r=lambda x: np.log(x.r_steady_px), log_q=lambda x: np.log(x.r_ss_proxy), log_p=lambda x: np.log(x.p_kpa))
        if len(g) < 15:
            continue
        cl = {"cov_type": "cluster", "cov_kwds": {"groups": pd.factorize(g.test_day)[0]}}
        m1 = smf.ols("log_r ~ log_q", g).fit(**cl)
        m2 = smf.ols("log_r ~ log_q + log_p", g).fit(**cl)
        ci = m1.conf_int().loc["log_q"]
        print(f"  {ft}: n={len(g)} ({g.test_day.nunique()} days)  slope {m1.params['log_q']:.2f} "
              f"(95 % CI {ci[0]:.2f} to {ci[1]:.2f}), R2 {m1.rsquared:.2f}, Spearman {g.r_steady_px.corr(g.r_ss_proxy, method='spearman'):.2f}")
        ci2 = m2.conf_int().loc["log_p"]
        print(f"      + pressure: slope q {m2.params['log_q']:.2f}, pressure exponent {m2.params['log_p']:.2f} "
              f"(95 % CI {ci2[0]:.2f} to {ci2[1]:.2f}), R2 {m2.rsquared:.2f}")


def glow_precursor(d: pd.DataFrame) -> None:
    print("\n### 3. Soot-glow fades before self-extinction?  (glow_half_before_off_s: yellow glow below half its peak)")
    s = d[d.flame_seen & d.extinction_mode.isin(["self_extinguished", "flow_terminated"]) & d.ignition_outcome.eq("yes")].copy()
    s["lead"] = s.glow_half_before_off_s.fillna(0.0)  # never halved before the end = no warning (0 s)
    for ft, g in s.groupby("flame_type"):
        print(f"  {ft}:")
        print(g.groupby("extinction_mode").lead.describe(percentiles=[0.25, 0.5, 0.75]).round(1).to_string())
        for thr in (3, 5, 10):
            se = g[g.extinction_mode.eq("self_extinguished")].lead >= thr
            ft_ = g[g.extinction_mode.eq("flow_terminated")].lead >= thr
            print(f"    warning >= {thr:>2} s before the end: self-extinguished {se.mean():.2f} (n={len(se)}), "
                  f"flow-cut {ft_.mean():.2f} (n={len(ft_)})")
        y = g.extinction_mode.eq("self_extinguished").astype(int).to_numpy()
        x = g.lead.to_numpy()
        auc = _auc(y, x)
        boot = stats.cluster_bootstrap(g.assign(y=y, x=x), lambda f: _auc(f.y.to_numpy(), f.x.to_numpy()), n_boot=1000)
        print(f"    AUC of the glow lead for 'will self-extinguish': {auc:.2f} (day-bootstrap 95 % CI {boot['ci_low']:.2f}-{boot['ci_high']:.2f})")


def _auc(y: np.ndarray, x: np.ndarray) -> float:
    from scipy.stats import rankdata

    pos, n1 = y == 1, int(y.sum())
    n0 = len(y) - n1
    return float((rankdata(x)[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 and n0 else np.nan


def shrinking(d: pd.DataFrame) -> None:
    print("\n### 4. Radius change in the last 5 s (relative to mid-life)")
    s = d[d.flame_seen & d.radius_quality.eq("ok") & d.ignition_outcome.eq("yes")]
    print(s.groupby(["flame_type", "extinction_mode"]).r_change_last_5s_rel.describe(percentiles=[0.25, 0.5, 0.75]).round(2).to_string())


def shrinking_lead(d: pd.DataFrame, source: str = "gs://flamesafe-psi-video/cfig-v2") -> None:
    """Is the flame already smaller 5-15 s BEFORE it ends? Radius relative to its own mid-life median, per window."""
    import io

    from flamesafe.pipeline import video

    print("\n### 5. Shrinking as an early warning (radius / mid-life radius, windows before the end)")
    out = video.Output(source)
    s = d[d.flame_seen & d.radius_quality.eq("ok") & d.ignition_outcome.eq("yes") & d.flame_visible_s.ge(20)
          & d.extinction_mode.isin(["self_extinguished", "flow_terminated"])]
    rows = []
    for r in s.itertuples():
        f = pd.read_parquet(io.BytesIO(out.read(f"frames/{r.video_key}.parquet")))
        f = f[f.r_eq_px.notna() & f.t_s.between(r.t_flame_on_s, r.t_flame_off_s)]
        mid = f[f.t_s.between(r.t_flame_on_s + 5, r.t_flame_on_s + 0.6 * r.flame_visible_s)].r_eq_px.median()
        win = {f"r_{a}_{b}s": f[f.t_s.between(r.t_flame_off_s - a, r.t_flame_off_s - b)].r_eq_px.median() / mid
               for a, b in ((15, 10), (10, 5), (5, 0))}
        rows.append({"test_day": r.test_day, "flame_type": r.flame_type, "mode": r.extinction_mode, **win})
    w = pd.DataFrame(rows)
    print(w.groupby(["flame_type", "mode"]).median(numeric_only=True).drop(columns="test_day").round(2).to_string())
    for ft, g in w.groupby("flame_type"):
        y = g["mode"].eq("self_extinguished").astype(int).to_numpy()
        if y.sum() < 5 or (1 - y).sum() < 5:
            print(f"  {ft}: too few flames of one outcome with a usable radius")
            continue
        for col in ("r_15_10s", "r_10_5s"):
            x = -g[col].to_numpy()
            ok = np.isfinite(x)
            b = stats.cluster_bootstrap(g[ok].assign(y=y[ok], x=x[ok]), lambda f: _auc(f.y.to_numpy(), f.x.to_numpy()), n_boot=1000)
            print(f"  {ft} {col}: AUC {_auc(y[ok], x[ok]):.2f} (day-bootstrap 95 % CI {b['ci_low']:.2f}-{b['ci_high']:.2f}), n={ok.sum()}")
        se, fc = g[g["mode"].eq("self_extinguished")], g[g["mode"].eq("flow_terminated")]
        print(f"  {ft}: radius < 80 % of mid-life 5-10 s before the end: self-extinguished {np.mean(se.r_10_5s < 0.8):.2f}, "
              f"flow-cut {np.mean(fc.r_10_5s < 0.8):.2f}")


def main() -> None:
    d = load()
    validate(d)
    radius_law(d)
    glow_precursor(d)
    shrinking(d)
    shrinking_lead(d)


if __name__ == "__main__":
    main()
