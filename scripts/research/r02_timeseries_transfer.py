"""Research iteration 2 (2026-11-15): what the per-test time series add (ADR-0005).

1. Validate the time-series flame detector against the PI table (CFI-G) and the script log (Flame Design).
2. Out-of-campaign test: fit the physical burn-time equation on CFI-G only, predict Flame Design without refitting.
3. Why the flow was cut (timer vs earlier cut) and burner temperature at the cut.
4. Oscillation right before the flame ended, self-extinguished vs flow-terminated flames.

Needs `flamesafe timeseries` + `flamesafe ts-features` (silver `acme__timeseries_features`) and gold.
Run: python scripts/research/r02_timeseries_transfer.py   (~2 min). Results: docs/03_data_science/RESEARCH_LOG.md.
"""

from __future__ import annotations

import warnings

import duckdb
import numpy as np
import pandas as pd

from flamesafe import config
from flamesafe.models import aft, m1
from flamesafe.physics.spherical_flame import add_spherical_groups

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
PHYSICAL = ["inv_tad", "log_p", "log_mtot", "log_L"]
FAMILY = "loglogistic"
MODES = ["self_extinguished", "flow_terminated"]
TIMER_GAP_S = (18, 30)  # the flow stops ~23 s before `flowTimeoutSec` when the timer ends the test (see log)


def load() -> pd.DataFrame:
    con = duckdb.connect(str(config.data_dir() / "gold" / "flamesafe.duckdb"), read_only=True)
    gas = con.sql("SELECT * FROM gas_flame_tests").df()
    con.close()
    ts = pd.read_parquet(config.data_dir() / "silver" / "tables" / "acme__timeseries_features.parquet")
    ts = ts[ts.file_variant.isna()].drop(columns=["source_file"])
    return gas.merge(ts, on=["psi_id", "test_id"], how="left")


def physical(d: pd.DataFrame) -> pd.DataFrame:
    d = add_spherical_groups(d)
    return d.assign(inv_tad=1000 / d.tad_k, log_p=np.log(d.p_kpa), log_mtot=np.log(d.m_tot_mg_s),
                    log_L=np.log(d.log_term)).dropna(subset=PHYSICAL)


def cohorts(j: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """CFI-G and Flame Design sustained flames with the same time-series definition of duration and outcome."""
    ok = j.ts_flame_class.eq("sustained") & j.x_fuel.gt(0) & ~j.test_id.isin(m1.AUDIT_EXCLUDED_TESTS)
    cfig = j[ok & j.campaign.eq("CFI-G") & j.ignition_outcome.eq("yes") & j.ts_extinction_mode.isin(MODES)].copy()
    cfig["mode"] = cfig.ts_extinction_mode
    fd = j[ok & j.campaign.eq("Flame Design") & j.qualifier.isna()].copy()  # ramp / low-O2 protocols kept apart
    logged = fd.tp_extinction_logged
    fd["mode"] = np.where(logged.notna(), np.where(logged.fillna(False).astype(bool), MODES[0], MODES[1]),
                          fd.ts_extinction_mode)
    fd = fd[fd["mode"].isin(MODES)]
    out = []
    for d in (cfig, fd):
        out.append(physical(d.assign(duration_s=d.flame_duration_s, event=d["mode"].eq(MODES[0]).astype(int))))
    return out[0], out[1]


def validate(j: pd.DataFrame) -> None:
    c = j[j.campaign.eq("CFI-G") & j.ts_flame_class.notna()]
    print("\n### 1. Detector validation")
    print("CFI-G, PI ignition outcome vs time-series flame class:")
    print(pd.crosstab(c.ignition_outcome.fillna("NA"), c.ts_flame_class))
    s = c[c.extinction_mode.notna() & c.ts_flame_class.eq("sustained") & c.ts_extinction_mode.isin(MODES)]
    d = s[s.burn_time_s.gt(0)]
    diff = (d.flame_duration_s - d.burn_time_s).abs()
    print(f"extinction mode agreement {np.mean(s.extinction_mode == s.ts_extinction_mode):.3f} (n={len(s)}); "
          f"burn time Spearman {d.flame_duration_s.corr(d.burn_time_s, method='spearman'):.3f}, "
          f"median |diff| {diff.median():.2f} s, within 2 s {np.mean(diff <= 2):.3f}")
    fd = j[j.campaign.eq("Flame Design") & j.ts_flame_class.eq("sustained") & j.tp_extinction_logged.notna()
           & j.ts_extinction_mode.isin(MODES)]
    agree = fd.ts_extinction_mode.eq(MODES[0]) == fd.tp_extinction_logged.astype(bool)
    print(f"Flame Design, agreement with the script's 'Extinction detected': {agree.mean():.3f} (n={len(fd)}); "
          f"non-ramp only: {agree[fd.qualifier.isna()].mean():.3f} (n={int(fd.qualifier.isna().sum())})")


def transfer(cfig: pd.DataFrame, fd: pd.DataFrame, n_boot: int = 400, seed: int = 26) -> None:
    print("\n### 2. Out-of-campaign transfer: fit on CFI-G, predict Flame Design (no refit)")
    print(fd.groupby(["flame_type", "fuel"]).agg(n=("event", "size"), self_ext=("event", "sum"),
                                                  days=("test_day", "nunique")).to_string())
    rng = np.random.default_rng(seed)
    for ft in ["normal", "inverse"]:
        a, b = cfig[cfig.flame_type == ft].reset_index(drop=True), fd[fd.flame_type == ft].reset_index(drop=True)
        fit = aft.fit_aft(a, PHYSICAL, FAMILY)
        loc = fit.predict_log_time(b)
        recal = aft.fit_aft(b.assign(pred=loc), ["pred"], FAMILY).coef
        null = aft.fit_aft(b, [], FAMILY).log_likelihood / len(b)
        cs, slopes, gains = [], [], []
        for _ in range(n_boot):
            aa = pd.concat([a[a.test_day == d] for d in rng.choice(a.test_day.unique(), a.test_day.nunique())])
            bb = pd.concat([b[b.test_day == d] for d in rng.choice(b.test_day.unique(), b.test_day.nunique())])
            f2 = aft.fit_aft(aa, PHYSICAL, FAMILY)
            l2 = f2.predict_log_time(bb)
            cs.append(m1.concordance(bb.duration_s, l2, bb.event))
            slopes.append(aft.fit_aft(bb.assign(pred=l2), ["pred"], FAMILY).coef["pred"])
            gains.append(f2.loglik(bb).mean() - aft.fit_aft(bb, [], FAMILY).log_likelihood / len(bb))
        ci = lambda v: f"[{np.quantile(v, 0.025):.2f}, {np.quantile(v, 0.975):.2f}]"  # noqa: E731
        print(f"\n{ft}: train CFI-G n={len(a)} ({a.test_day.nunique()} days) -> test Flame Design n={len(b)} "
              f"({b.test_day.nunique()} days)")
        print(f"  C-index {m1.concordance(b.duration_s, loc, b.event):.3f} {ci(cs)}")
        print(f"  calibration: ln t_obs = {recal['Intercept']:.2f} + {recal['pred']:.2f} * ln t_pred, slope CI {ci(slopes)}")
        print(f"  log-lik/obs: transfer {fit.loglik(b).mean():.3f} vs no-covariate model fitted on Flame Design {null:.3f}; "
              f"gain CI {ci(gains)}")
        print("  CFI-G coefficients:", fit.coef.round(2).to_dict())
        print("  Flame Design own fit:", aft.fit_aft(b, PHYSICAL, FAMILY).coef.round(2).to_dict())


def flow_cut_causes(j: pd.DataFrame) -> None:
    print("\n### 3. Why was the flow cut?")
    s = j[j.ts_flame_class.eq("sustained") & j.ts_extinction_mode.eq("flow_terminated") & j.qualifier.isna()].copy()
    gap = s.cfg_flow_timeout_s - s.flow_duration_s
    s["cause"] = np.where(gap.between(*TIMER_GAP_S), "timer", "before timer")
    print(s.groupby(["campaign", "flame_type", "cause"]).agg(
        n=("test_id", "size"), flame_s_median=("flame_duration_s", "median"),
        burner_peak_k_median=("peak_burner_t_k", "median")).round(1).to_string())
    se = j[j.campaign.eq("CFI-G") & j.extinction_mode.eq("self_extinguished")]
    print(f"CFI-G self-extinguished flames, burner peak median: {se.peak_burner_t_k.median():.0f} K")


def oscillation(j: pd.DataFrame) -> None:
    print("\n### 4. Oscillation right before the flame ended (sustained, non-ramp)")
    s = j[j.ts_flame_class.eq("sustained") & j.qualifier.isna() & j.ts_extinction_mode.isin(MODES)].copy()
    s["lead"] = s[["pmt_osc_lead_s", "rad_osc_lead_s"]].max(axis=1)
    for thr in (2, 5):
        t = s.assign(osc=s.lead >= thr).groupby(["campaign", "flame_type", "ts_extinction_mode"]).osc.agg(["mean", "size"])
        print(f"share oscillating for >= {thr} s before the end:")
        print(t.round(2).to_string())
    e = s[s.ts_extinction_mode.eq(MODES[0]) & (s.lead >= 2)]
    print("lead time (s) among oscillating self-extinctions:", e.lead.describe().round(1).to_dict())


def main() -> None:
    j = load()
    print(f"gold tests with a time series: {int(j.ts_flame_class.notna().sum())} of {len(j)}")
    validate(j)
    cfig, fd = cohorts(j)
    transfer(cfig, fd)
    flow_cut_causes(j)
    oscillation(j)


if __name__ == "__main__":
    main()
