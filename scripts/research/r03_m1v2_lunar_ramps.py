"""Research iteration 3 (2026-11-15): M1 v2, first lunar-base reading and the flow-ramp tests.

1. Thermochemistry check: calculated Zst / Tad vs the investigators' columns.
2. M1 v2 for normal flames: physical log-logistic equation on CFI-G + Flame Design (same time-series definition),
   with a sensitivity analysis for flow cuts caused by the burner temperature limit (informative censoring).
3. Reference atmospheres placed on the physical axes (Tad, pressure, burner flow, L): is the lunar base inside the
   tested region, and what burn duration does the equation give there?
4. Flow-ramp tests (Flame Design): burner flow and flame temperature at the moment of extinction.

Needs gold, `flamesafe timeseries` + `flamesafe ts-features`, and Cantera (extra `analysis`).
Run: python scripts/research/r03_m1v2_lunar_ramps.py   (~4 min). Results: docs/03_data_science/RESEARCH_LOG.md.
"""

from __future__ import annotations

import warnings

import duckdb
import numpy as np
import pandas as pd

from flamesafe import config
from flamesafe.models import aft, m1
from flamesafe.physics import thermochem as tc
from flamesafe.physics.atmospheres import REFERENCE_ATMOSPHERES
from flamesafe.physics.spherical_flame import M_N2, MOLAR_MASS_G_MOL, add_spherical_groups
from flamesafe.pipeline import timeseries as ts

warnings.filterwarnings("ignore")
pd.set_option("display.width", 230)
PHYSICAL = ["inv_tad", "log_p", "log_mtot", "log_L"]
FAMILY = "loglogistic"
MODES = ["self_extinguished", "flow_terminated"]
TIMER_GAP_S = (18, 30)
SOURCE = {"x_fuel": 0.3, "m_fuel_mg_s": 1.0}  # typical CFI-G burner stream: 30 % fuel in N2, 1 mg/s of fuel
ATMOSPHERES = ["iss_cabin", "exploration_8p2_34", "lunar_base_upper"]


def load() -> pd.DataFrame:
    con = duckdb.connect(str(config.data_dir() / "gold" / "flamesafe.duckdb"), read_only=True)
    gas = con.sql("SELECT * FROM gas_flame_tests").df()
    con.close()
    feats = pd.read_parquet(config.data_dir() / "silver" / "tables" / "acme__timeseries_features.parquet")
    return gas.merge(feats[feats.file_variant.isna()].drop(columns=["source_file"]), on=["psi_id", "test_id"], how="left")


def physical(d: pd.DataFrame) -> pd.DataFrame:
    d = add_spherical_groups(d)
    return d.assign(inv_tad=1000 / d.tad_k, log_p=np.log(d.p_kpa), log_mtot=np.log(d.m_tot_mg_s),
                    log_L=np.log(d.log_term)).dropna(subset=PHYSICAL)


def normal_cohort(j: pd.DataFrame) -> pd.DataFrame:
    """Sustained normal flames of both campaigns, non-ramp, with the cause of the flow cut."""
    ok = (j.flame_type.eq("normal") & j.ts_flame_class.eq("sustained") & j.x_fuel.gt(0) & j.qualifier.isna()
          & ~j.test_id.isin(m1.AUDIT_EXCLUDED_TESTS) & (j.campaign.eq("Flame Design") | j.ignition_outcome.eq("yes")))
    d = j[ok].copy()
    logged = d.tp_extinction_logged
    d["mode"] = np.where(d.campaign.eq("Flame Design") & logged.notna(),
                         np.where(logged.fillna(False).astype(bool), MODES[0], MODES[1]), d.ts_extinction_mode)
    d = d[d["mode"].isin(MODES)]
    timer = (d.cfg_flow_timeout_s - d.flow_duration_s).between(*TIMER_GAP_S)
    d["end_cause"] = np.where(d["mode"].eq(MODES[0]), "self_extinguished", np.where(timer, "timer", "cut_before_timer"))
    d["timer_limit_s"] = d.cfg_flow_timeout_s - np.mean(TIMER_GAP_S) - d.ignition_delay_s.clip(lower=0)
    d = d.assign(duration_s=d.flame_duration_s, event=d["mode"].eq(MODES[0]).astype(int),
                 is_fd=d.campaign.eq("Flame Design").astype(float),
                 day=d.campaign.str[:1] + d.test_day.astype(str))
    return physical(d).reset_index(drop=True)


# ------------------------------------------------------------------------------------------------ 1. thermochemistry
def check_thermochem(j: pd.DataFrame) -> None:
    print("\n### 1. Calculated Zst / Tad vs the investigators' columns")
    d = j.dropna(subset=["x_fuel", "xo2", "tad_k", "zst", "p_kpa"])
    d = d[d.x_fuel.gt(0)]
    z = np.array([tc.zst(f, x, o) for f, x, o in zip(d.fuel, d.x_fuel, d.xo2, strict=True)])
    t = np.array([tc.tad_k(f, x, o, p) for f, x, o, p in zip(d.fuel, d.x_fuel, d.xo2, d.p_kpa, strict=True)])
    dt = t - d.tad_k.to_numpy()
    print(f"n={len(d)}; Zst max |diff| {np.abs(z - d.zst).max():.4f}; Tad median diff {np.median(dt):+.1f} K, "
          f"90 % within [{np.quantile(dt, 0.05):+.0f}, {np.quantile(dt, 0.95):+.0f}] K, corr {np.corrcoef(t, d.tad_k)[0, 1]:.4f}")


# ------------------------------------------------------------------------------------------------ 2. M1 v2
def scenarios(d: pd.DataFrame) -> dict[str, pd.DataFrame]:
    thermal = d.end_cause.eq("cut_before_timer") & d.campaign.eq("CFI-G")  # burner limit (~728 K), see R10
    extended = d.copy()
    extended.loc[thermal, "duration_s"] = np.fmax(d.duration_s, d.timer_limit_s)[thermal]
    return {"A all cuts are censoring": d, "B drop thermal-limit cuts": d[~thermal],
            "C thermal cuts would have reached the timer": extended}


def m1_v2(d: pd.DataFrame) -> dict[str, pd.DataFrame]:
    print("\n### 2. M1 v2 (normal flames, both campaigns, physical log-logistic)")
    print(pd.crosstab(d.campaign, d.end_cause))
    sc = scenarios(d)
    cols = PHYSICAL + ["is_fd"]
    rows = {}
    for name, data in sc.items():
        rows[name] = aft.fit_aft(data, cols, FAMILY).coef
    print("\ncoefficients by censoring scenario:")
    print(pd.DataFrame(rows).round(2).to_string())
    base = sc["A all cuts are censoring"].reset_index(drop=True)
    print("\nscenario A with day-bootstrap 95 % CI:")
    print(aft.bootstrap_coef(base, cols, FAMILY, groups="day", n_boot=500).round(2).to_string())
    ll, loc = aft.grouped_oof_loglik(base, cols, FAMILY, groups="day")
    nll, _ = aft.grouped_oof_loglik(base, ["is_fd"], FAMILY, groups="day")
    oll, oloc = aft.grouped_oof_loglik(base, ["xo2", "log_p", "is_fd"], FAMILY, groups="day")
    print(f"\nleave-one-day-out (n={len(base)}, {base.day.nunique()} days): physical ll/obs {ll.mean():.3f}, "
          f"C {m1.concordance(base.duration_s, loc, base.event):.3f} | O2 + pressure {oll.mean():.3f}, "
          f"C {m1.concordance(base.duration_s, oloc, base.event):.3f} | campaign only {nll.mean():.3f}")
    for horizon in (30.0, 60.0):  # calibration of P(still burning at t) by tertile of predicted probability
        usable = (base.duration_s >= horizon) | base.event.eq(1)  # outcome at `horizon` is known
        b = base[usable]
        sigma = np.exp(aft.fit_aft(base, cols, FAMILY).coef["log_sigma"])
        p = 1 / (1 + np.exp((np.log(horizon) - loc[usable.to_numpy()]) / sigma))
        obs = (b.duration_s >= horizon).astype(float)
        cal = pd.DataFrame({"p": p, "obs": obs, "bin": pd.qcut(p, 3, labels=False, duplicates="drop")}).groupby("bin").agg(
            predicted=("p", "mean"), observed=("obs", "mean"), n=("obs", "size"))
        print(f"out-of-fold calibration, P(burning at {horizon:.0f} s), n={len(b)}:")
        print(cal.round(2).to_string())
    return sc


# ------------------------------------------------------------------------------------------------ 3. habitats
def habitat_rows() -> pd.DataFrame:
    rows = []
    for key in ATMOSPHERES:
        a = REFERENCE_ATMOSPHERES[key]
        for fuel in ("ethane", "propane", "butane"):
            y = SOURCE["x_fuel"] * MOLAR_MASS_G_MOL[fuel] / (SOURCE["x_fuel"] * MOLAR_MASS_G_MOL[fuel] + 0.7 * M_N2)
            zst = tc.zst(fuel, SOURCE["x_fuel"], a.o2_mole_fraction)
            rows.append({"atmosphere": a.name, "fuel": fuel, "xo2": a.o2_mole_fraction, "p_kpa": a.total_pressure_kpa,
                         "tad_k": tc.tad_k(fuel, SOURCE["x_fuel"], a.o2_mole_fraction, a.total_pressure_kpa),
                         "zst": zst, "m_tot_mg_s": SOURCE["m_fuel_mg_s"] / y, "log_term": -np.log(1 - zst), "is_fd": 0.0})
    h = pd.DataFrame(rows)
    return h.assign(inv_tad=1000 / h.tad_k, log_p=np.log(h.p_kpa), log_mtot=np.log(h.m_tot_mg_s), log_L=np.log(h.log_term))


def habitats(sc: dict[str, pd.DataFrame], n_boot: int = 400, seed: int = 26) -> None:
    print("\n### 3. Reference atmospheres on the physical axes")
    h = habitat_rows()
    train = sc["A all cuts are censoring"].reset_index(drop=True)
    cfig = train[train.campaign.eq("CFI-G")]
    # support: where each atmosphere falls within the tested range of every physical axis, and close neighbours
    mu, sd = train[PHYSICAL].mean(), train[PHYSICAL].std()
    zt, zh = (train[PHYSICAL] - mu) / sd, (h[PHYSICAL] - mu) / sd
    dist = np.sqrt(((zh.to_numpy()[:, None, :] - zt.to_numpy()[None, :, :]) ** 2).sum(axis=2))
    self_dist = np.sqrt(((zt.to_numpy()[:, None, :] - zt.to_numpy()[None, :, :]) ** 2).sum(axis=2))
    typical = np.sort(self_dist, axis=1)[:, 5].mean()  # mean distance to the 5th nearest test, among the tests
    support = h[["atmosphere", "fuel", "tad_k", "zst", "p_kpa"]].copy()
    for col in PHYSICAL:
        support[f"pct_{col}"] = [(train[col] < v).mean() for v in h[col]]
    support["tests_within_1sd"] = (dist < 1.0).sum(axis=1)
    support["days_within_1sd"] = [train.day[row < 1.0].nunique() for row in dist]
    support["dist_5th_nearest_vs_typical"] = np.sort(dist, axis=1)[:, 4] / typical
    near_o2p = [len(m1.nearby_tests(cfig, r.xo2, r.p_kpa)) for r in h.itertuples()]
    support["tests_near_in_o2_and_p"] = near_o2p
    print(support.round(2).to_string(index=False))

    cols = PHYSICAL + ["is_fd"]
    out = h[["atmosphere", "fuel"]].copy()
    rng = np.random.default_rng(seed)
    for name, data in sc.items():
        data = data.reset_index(drop=True)
        fit = aft.fit_aft(data, cols, FAMILY)
        out[f"median_s {name[0]}"] = np.exp(fit.predict_log_time(h)).round(0)
        if name.startswith("A"):
            days, draws_med, draws_p60 = data.day.unique(), [], []
            for _ in range(n_boot):
                sample = pd.concat([data[data.day == d] for d in rng.choice(days, len(days))], ignore_index=True)
                f2 = aft.fit_aft(sample, cols, FAMILY)
                draws_med.append(np.exp(f2.predict_log_time(h)))
                draws_p60.append(f2.survival(h, 60.0))
            lo, hi = np.quantile(draws_med, [0.05, 0.95], axis=0)
            out["median 90% CI"] = [f"{a:.0f}-{b:.0f}" for a, b in zip(lo, hi, strict=True)]
            out["P(burning at 60 s)"] = fit.survival(h, 60.0).round(2)
            lo, hi = np.quantile(draws_p60, [0.05, 0.95], axis=0)
            out["P60 90% CI"] = [f"{a:.2f}-{b:.2f}" for a, b in zip(lo, hi, strict=True)]
    print("\npredicted burn duration (CFI-G reference level, source: 30 % fuel in N2 at 1 mg/s):")
    print(out.to_string(index=False))
    print("\nempirical check, CFI-G tests near each atmosphere in O2 and pressure (median of self-extinguished | n):")
    for key in ATMOSPHERES:
        a = REFERENCE_ATMOSPHERES[key]
        near = m1.nearby_tests(cfig, a.o2_mole_fraction, a.total_pressure_kpa)
        print(f"  {a.name}: n={len(near)}, self-extinguished {int(near.event.sum())}, "
              f"median duration {near.duration_s.median() if len(near) else float('nan'):.0f} s")


# ------------------------------------------------------------------------------------------------ 4. ramps
def ramps(j: pd.DataFrame) -> None:
    print("\n### 4. Flow-ramp tests (Flame Design, normal ethylene flames)")
    root = config.data_dir() / "bronze" / "files" / "PSI-10"

    def volts(test_id: str, t0: float, t1: float) -> tuple[float, float, float]:
        meta, d = ts.parse_stream(root / f"PSI-10_Raw Data_{test_id}_data.csv")
        w = d[(d.t >= t0) & (d.t <= t1)]
        return w["MFCA3FuelFlow"].median(), w["MFCA2BypassFlow"].median(), float(meta.get("MFCA2 Full Scale", "nan"))

    ref = j[j.campaign.eq("Flame Design") & j.flame_type.eq("normal") & j.qualifier.isna() & j.fuel.eq("ethylene")
            & j.ts_flame_class.eq("sustained") & j.flame_duration_s.gt(15)].dropna(subset=["m_fuel_mg_s", "m_n2_mg_s"])
    cal = []
    for r in ref.itertuples():
        v3, v2, fs2 = volts(r.test_id, r.t_ignition_s + 6, r.t_flame_end_s - 3)
        cal.append({"k_fuel": r.m_fuel_mg_s / v3, "k_n2": r.m_n2_mg_s / (v2 * fs2) if r.m_n2_mg_s > 0.05 else np.nan})
    cal = pd.DataFrame(cal)
    k_fuel, k_n2 = cal.k_fuel.median(), cal.k_n2.median()
    print(f"MFC calibration from {len(cal)} steady tests: fuel {k_fuel:.4f} mg/s per V "
          f"(spread {cal.k_fuel.std() / k_fuel:.1%}); N2 {k_n2:.3f} mg/s per (V x full scale) "
          f"(spread {cal.k_n2.std() / k_n2:.1%}, n={int(cal.k_n2.notna().sum())})")

    r = j[j.campaign.eq("Flame Design") & j.flame_type.eq("normal") & j.qualifier.isin(["RAMP", "RAMPED"])
          & j.ts_flame_class.eq("sustained") & j.tp_extinction_logged.fillna(False).astype(bool)]
    rows = []
    for x in r.itertuples():
        v3a, v2a, fs2 = volts(x.test_id, x.t_ignition_s + 5, x.t_ignition_s + 9)
        v3b, v2b, _ = volts(x.test_id, x.t_flame_end_s - 1.0, x.t_flame_end_s)
        row = {"test_id": x.test_id, "xo2": x.xo2, "p_kpa": x.p_kpa, "duration_s": x.flame_duration_s}
        for tag, v3, v2 in (("start", v3a, v2a), ("ext", v3b, v2b)):
            mf, mn = k_fuel * max(v3, 0), k_n2 * max(v2, 0) * fs2
            xf = (mf / MOLAR_MASS_G_MOL["ethylene"]) / (mf / MOLAR_MASS_G_MOL["ethylene"] + mn / M_N2) if mf > 0 else np.nan
            row |= {f"m_tot_{tag}": mf + mn, f"x_fuel_{tag}": xf}
        if row["x_fuel_ext"] > 0.02 and row["m_tot_ext"] > 0.02:
            row["tad_ext_k"] = tc.tad_k("ethylene", row["x_fuel_ext"], x.xo2, x.p_kpa)
            row["tad_start_k"] = tc.tad_k("ethylene", row["x_fuel_start"], x.xo2, x.p_kpa)
            row["L_ext"] = -np.log(1 - tc.zst("ethylene", row["x_fuel_ext"], x.xo2))
        rows.append(row)
    t = pd.DataFrame(rows).dropna(subset=["tad_ext_k"])
    t["flow_ratio"] = t.m_tot_ext / t.m_tot_start
    t["kind"] = np.where(t.flow_ratio < 0.8, "flow ramped down", "composition ramped")
    print(f"ramp tests with a logged extinction and usable flows: {len(t)} of {len(r)}")
    print(t.groupby("kind").agg(n=("test_id", "size"), xo2=("xo2", "median"), flow_ratio=("flow_ratio", "median"),
                                m_tot_ext=("m_tot_ext", "median"), x_fuel_start=("x_fuel_start", "median"),
                                x_fuel_ext=("x_fuel_ext", "median"), tad_start=("tad_start_k", "median"),
                                tad_ext=("tad_ext_k", "median")).round(3).to_string())
    for kind, g in t.groupby("kind"):
        print(f"\n{kind}: at extinction")
        print(g[["m_tot_ext", "tad_ext_k", "x_fuel_ext", "flow_ratio"]].describe().loc[["min", "25%", "50%", "75%", "max"]].round(3).to_string())
        if len(g) >= 8:
            print(f"  Spearman(m_tot at extinction, Tad at extinction) = {g.m_tot_ext.corr(g.tad_ext_k, method='spearman'):.2f}; "
                  f"with xo2 = {g.m_tot_ext.corr(g.xo2, method='spearman'):.2f}")


def main() -> None:
    j = load()
    check_thermochem(j)
    d = normal_cohort(j)
    sc = m1_v2(d)
    habitats(sc)
    ramps(j)


if __name__ == "__main__":
    main()
