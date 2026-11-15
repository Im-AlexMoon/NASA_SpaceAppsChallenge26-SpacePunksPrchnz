"""Research iteration 1 (2026-11-15): physics-based equation for flame burn duration, CFI-G spherical flames.

Run: python scripts/research/r01_physics_burn_time.py   (reads gold DuckDB, read-only; ~1 min)
Results are recorded in docs/03_data_science/RESEARCH_LOG.md.
"""

from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from flamesafe import config
from flamesafe.models import aft, m1
from flamesafe.physics.spherical_flame import add_spherical_groups

pd.set_option("display.width", 200)
FAMILY = "loglogistic"
SETS = {
    "null": [],
    "O2 only": ["xo2"],
    "empirical M1": ["xo2", "log_p", "log_xfuel", "log_flow", "is_ethane", "is_propane"],
    "physical": ["inv_tad", "log_p", "log_mtot", "log_L"],
    "physical + fuel": ["inv_tad", "log_p", "log_mtot", "log_L", "is_ethane", "is_propane"],
}


def load() -> pd.DataFrame:
    con = duckdb.connect(str(config.data_dir() / "gold" / "flamesafe.duckdb"), read_only=True)
    gas = con.sql("SELECT * FROM gas_flame_tests").df()
    con.close()
    d = add_spherical_groups(m1.survival_cohort(gas))
    return d.assign(inv_tad=1000 / d.tad_k, log_mtot=np.log(d.m_tot_mg_s), log_L=np.log(d.log_term),
                    is_ethane=d.fuel.eq("ethane").astype(float), is_propane=d.fuel.eq("propane").astype(float))


def day_bootstrap_mean(values: np.ndarray, days: np.ndarray, n_boot: int = 2000, seed: int = 26) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    index = {k: np.flatnonzero(days == k) for k in pd.unique(days)}
    keys = list(index)
    means = [values[np.concatenate([index[k] for k in rng.choice(keys, len(keys))])].mean() for _ in range(n_boot)]
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def main() -> None:
    data = load()
    for flame_type, d in data.groupby("flame_type"):
        d = d.reset_index(drop=True)
        print(f"\n===== {flame_type}: n={len(d)}, events={int(d.event.sum())}, days={d.test_day.nunique()}")
        rows, oof = [], {}
        for family in aft.FAMILIES:
            for name, cols in SETS.items():
                ll, loc = aft.grouped_oof_loglik(d, cols, family)
                if family == FAMILY:
                    oof[name] = ll
                rows.append({"family": family, "model": name, "k": len(cols) + 2, "aic": aft.fit_aft(d, cols, family).aic,
                             "oof_ll_per_obs": ll.mean(), "worst_obs_ll": ll.min(),
                             "oof_c": m1.concordance(d.duration_s, loc, d.event) if cols else 0.5})
        print(pd.DataFrame(rows).round(3).to_string(index=False))
        for a, b in [("physical", "empirical M1"), ("physical + fuel", "empirical M1"), ("physical", "O2 only")]:
            diff = oof[a] - oof[b]
            lo, hi = day_bootstrap_mean(diff, d.test_day.to_numpy())
            print(f"OOF ll/obs, {a} minus {b}: {diff.mean():+.3f}  CI95 [{lo:+.3f}, {hi:+.3f}]")
        for name in ["physical", "physical + fuel"]:
            print(name, FAMILY)
            print(aft.bootstrap_coef(d, SETS[name], FAMILY, n_boot=600).round(2).to_string())


if __name__ == "__main__":
    main()
