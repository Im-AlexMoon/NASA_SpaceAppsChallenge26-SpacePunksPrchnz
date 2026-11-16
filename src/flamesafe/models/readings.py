"""M-01 v2 · Atmosphere readings with evidence tiers (ADR-0007): burn duration of a spherical gas flame in microgravity.

The model is the physical log-logistic burn-time law of RESEARCH_LOG R13, fitted on sustained **normal** flames of both
ACME campaigns (CFI-G + Flame Design, same time-series definition of duration):

    ln t = b0 + b1 (1000/Tad) + b2 ln p + b3 ln m_tot + b4 ln L + b5 [Flame Design] + sigma * logistic

`train()` produces a small JSON artifact (coefficients, day-bootstrap draws, training domain, metrics, provenance and the
PHY review); `read()` turns a cabin atmosphere plus a fuel source into a reading with one of three evidence tiers:

* **A · measured nearby** — >= 5 real CFI-G normal-flame tests from >= 2 days within ±0.05 O2 and ±25 % pressure.
  The observed values come first; the model is shown as a comparison.
* **B · model interpolation** — no nearby tests, but every physical input inside the tested range and close enough to the
  training data. The model value with its 90 % interval and the warning "no nearby tests".
* **C · no evidence** — outside the tested range, untested fuel, or partial gravity for the gravity effect. No number.

Everything is microgravity. Partial gravity (Moon, Mars) is always tier C for the effect of gravity (PHY-05).
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd

from flamesafe.models import aft, m1
from flamesafe.physics import thermochem as tc
from flamesafe.physics.spherical_flame import M_N2, MOLAR_MASS_G_MOL, add_spherical_groups

MODEL_ID = "M-01-v2-burn-time"
FAMILY = "loglogistic"
PHYSICAL = ["inv_tad", "log_p", "log_mtot", "log_L"]
FEATURES = PHYSICAL + ["is_fd"]
MODES = ("self_extinguished", "flow_terminated")
FUELS = ("ethane", "propane", "butane")
DEFAULT_SOURCE = {"fuel": "propane", "x_fuel": 0.3, "m_fuel_mg_s": 1.0}  # typical CFI-G burner stream
GRAVITY = ("microgravity", "moon", "mars", "earth")
NEAR_DXO2, NEAR_REL_P, NEAR_MIN_TESTS, NEAR_MIN_DAYS = 0.05, 0.25, 5, 2
MAX_DISTANCE_RATIO = 3.0  # tier B only if the 5th-nearest training flame is < 3x the typical spacing between tests
ARTIFACT = Path(__file__).with_name("artifacts") / "m1v2_burn_time.json"


# --------------------------------------------------------------------------------------------------------- training

def _physical(d: pd.DataFrame) -> pd.DataFrame:
    d = add_spherical_groups(d)
    return d.assign(inv_tad=1000 / d.tad_k, log_p=np.log(d.p_kpa), log_mtot=np.log(d.m_tot_mg_s),
                    log_L=np.log(d.log_term)).dropna(subset=PHYSICAL)


def training_cohort(gas: pd.DataFrame, ts: pd.DataFrame) -> pd.DataFrame:
    """Sustained, non-ramp normal flames of CFI-G and Flame Design with the time-series duration and outcome."""
    ts = ts[ts.file_variant.isna()].drop(columns=["source_file"], errors="ignore")
    j = gas.merge(ts, on=["psi_id", "test_id"], how="inner")
    ok = (j.flame_type.eq("normal") & j.ts_flame_class.eq("sustained") & j.x_fuel.gt(0) & j.qualifier.isna()
          & ~j.test_id.isin(m1.AUDIT_EXCLUDED_TESTS) & (j.campaign.eq("Flame Design") | j.ignition_outcome.eq("yes")))
    d = j[ok].copy()
    logged = d.tp_extinction_logged
    d["mode"] = np.where(d.campaign.eq("Flame Design") & logged.notna(),
                         np.where(logged.fillna(False).astype(bool), MODES[0], MODES[1]), d.ts_extinction_mode)
    d = d[d["mode"].isin(MODES)]
    d = d.assign(duration_s=d.flame_duration_s, event=d["mode"].eq(MODES[0]).astype(int),
                 is_fd=d.campaign.eq("Flame Design").astype(float), day=d.campaign.str[:1] + d.test_day.astype(str))
    return _physical(d).reset_index(drop=True)


def _sha(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def train(gas: pd.DataFrame, ts: pd.DataFrame, n_boot: int = 400, seed: int = 26,
          provenance: dict | None = None, review: dict | None = None) -> dict:
    """Fit the model, its day-bootstrap draws and leave-one-day-out metrics; return the JSON-ready artifact."""
    d = training_cohort(gas, ts)
    fit = aft.fit_aft(d, FEATURES, FAMILY)
    boot = aft.bootstrap_coef(d, FEATURES, FAMILY, groups="day", n_boot=n_boot, seed=seed)
    rng = np.random.default_rng(seed)
    keys = d.day.unique()
    idx = {k: np.flatnonzero(d.day.to_numpy() == k) for k in keys}
    draws = []
    converged = 0
    for _ in range(n_boot):
        rows = np.concatenate([idx[k] for k in rng.choice(keys, size=len(keys), replace=True)])
        draw = aft.fit_aft(d.iloc[rows], FEATURES, FAMILY)
        converged += int(draw.converged)
        draws.append(draw.theta.round(6).tolist())
    ll, loc = aft.grouped_oof_loglik(d, FEATURES, FAMILY, groups="day")
    base_ll, _ = aft.grouped_oof_loglik(d, ["is_fd"], FAMILY, groups="day")
    mu, sd = d[PHYSICAL].mean(), d[PHYSICAL].std()
    z = ((d[PHYSICAL] - mu) / sd).to_numpy()
    dist = np.sqrt(((z[:, None, :] - z[None, :, :]) ** 2).sum(axis=2))
    typical = float(np.sort(dist, axis=1)[:, 5].mean())
    return {
        "model_id": MODEL_ID, "family": FAMILY, "features": FEATURES, "theta": fit.theta.round(6).tolist(),
        "coef_table": boot.round(4).reset_index(names="term").to_dict("records"), "bootstrap_draws": draws,
        "domain": {"min": d[PHYSICAL].min().round(5).to_dict(), "max": d[PHYSICAL].max().round(5).to_dict(),
                   "mean": mu.round(6).to_dict(), "sd": sd.round(6).to_dict(), "train_z": z.round(4).tolist(),
                   "typical_5th_nn_distance": round(typical, 4)},
        "cohort": {"n": int(len(d)), "events": int(d.event.sum()), "days": int(d.day.nunique()),
                   "by_campaign": d.groupby("campaign").size().to_dict()},
        "metrics": {"oof_loglik_per_obs": round(float(ll.mean()), 4),
                    "oof_loglik_campaign_only": round(float(base_ll.mean()), 4),
                    "oof_c_index": round(m1.concordance(d.duration_s, loc, d.event), 4),
                    "validation": "leave-one-operations-day-out"},
        "fit_diagnostics": {"converged": fit.converged, "bootstrap_finite": len(draws), "bootstrap_converged": converged},
        "reference_level": "CFI-G (is_fd = 0)",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "provenance": provenance or {}, "review": review or {"status": "candidate"},
    }


def save(artifact: dict, path: Path = ARTIFACT) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(artifact, indent=1, sort_keys=True, allow_nan=False) + "\n",
                             encoding="utf-8", newline="\n")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def load(path: Path = ARTIFACT) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------------------- reading

def source_features(xo2: float, p_kpa: float, fuel: str, x_fuel: float, m_fuel_mg_s: float) -> dict[str, float]:
    """Physical inputs of a normal spherical flame (fuel stream into the cabin atmosphere). Tad/Zst are calculated."""
    zst = tc.zst(fuel, x_fuel, xo2)
    tad = tc.tad_k(fuel, x_fuel, xo2, p_kpa)
    w = MOLAR_MASS_G_MOL[fuel]
    y_fuel = x_fuel * w / (x_fuel * w + (1 - x_fuel) * M_N2)
    m_tot = m_fuel_mg_s / y_fuel
    log_term = -np.log(1 - zst)
    return {"tad_k": tad, "zst": zst, "m_tot_mg_s": m_tot, "inv_tad": 1000 / tad, "log_p": float(np.log(p_kpa)),
            "log_mtot": float(np.log(m_tot)), "log_L": float(np.log(log_term)), "is_fd": 0.0}


def _predict(theta: np.ndarray, x: np.ndarray, t: float | None = None):
    loc = theta[0] + x @ theta[1:-1]
    if t is None:
        return np.exp(loc)
    return 1 / (1 + np.exp((np.log(t) - loc) / np.exp(theta[-1])))


def nearby_evidence(gas: pd.DataFrame, xo2: float, p_kpa: float, fuel: str | None = None) -> dict[str, object]:
    """Real CFI-G normal-flame tests near the atmosphere: counts, observed ignition and burn durations."""
    g = gas[gas.campaign.eq("CFI-G") & gas.flame_type.eq("normal") & gas.x_fuel.gt(0)]
    near = g[g.xo2.sub(xo2).abs().le(NEAR_DXO2) & g.p_kpa.sub(p_kpa).abs().le(NEAR_REL_P * p_kpa)]
    known = near[near.ignition_outcome.isin(["yes", "no"])]
    lit = near[near.ignition_outcome.eq("yes") & near.burn_time_s.gt(0)
               & near.extinction_mode.isin(["self_extinguished", "flow_terminated"])]
    se = lit[lit.extinction_mode.eq("self_extinguished")]
    tests = (near.sort_values("test_id")[["test_id", "test_day", "fuel", "xo2", "p_kpa", "ignition_outcome",
                                          "burn_time_s", "extinction_mode"]]
             .replace({np.nan: None}).to_dict("records"))
    return {
        "window": {"xo2_plus_minus": NEAR_DXO2, "pressure_relative": NEAR_REL_P},
        "n_tests": int(len(near)), "n_days": int(near.test_day.nunique()) if len(near) else 0,
        "n_known_ignition": int(len(known)),
        "n_ignited": int(known.ignition_outcome.eq("yes").sum()),
        "ignition_rate": round(float(known.ignition_outcome.eq("yes").mean()), 3) if len(known) else None,
        "n_burning": int(len(lit)), "n_flow_cut": int(lit.extinction_mode.eq("flow_terminated").sum()),
        "n_self_extinguished": int(len(se)),
        "median_burn_s_self_extinguished": round(float(se.burn_time_s.median()), 1) if len(se) else None,
        "same_fuel_tests": int(near.fuel.eq(fuel).sum()) if fuel else None,
        "fuel_counts": {str(name): int(count) for name, count in near.fuel.value_counts().items()},
        "tests": tests,
    }


def read(artifact: dict, xo2: float, p_kpa: float, gas: pd.DataFrame | None = None, fuel: str = "propane",
         x_fuel: float = 0.3, m_fuel_mg_s: float = 1.0, gravity: str = "microgravity",
         label: str | None = None) -> dict[str, object]:
    """Reading for one atmosphere + fuel source. Values are withheld (None) at tier C."""
    if gravity not in GRAVITY:
        raise ValueError(f"gravity must be one of {GRAVITY}")
    if not (0 < xo2 <= 1 and 0 < x_fuel <= 1 and p_kpa > 0 and m_fuel_mg_s > 0):
        raise ValueError("xo2 and x_fuel are mole fractions in (0, 1]; pressure and fuel flow must be positive")
    caveats = ["The model describes microgravity. The analyzed tests do not validate a gravity effect.",
               "Burn duration of a laboratory spherical gas flame, not the time available to respond to a fire.",
               "Tad and Zst are calculated (chemical equilibrium), not measured."]
    out: dict[str, object] = {"label": label, "inputs": {"xo2": xo2, "p_kpa": p_kpa, "po2_kpa": round(xo2 * p_kpa, 3),
                              "fuel": fuel, "x_fuel": x_fuel, "m_fuel_mg_s": m_fuel_mg_s, "gravity": gravity},
                              "model_id": artifact["model_id"], "review": artifact.get("review", {}),
                              "regime": "microgravity"}
    near = nearby_evidence(gas, xo2, p_kpa, fuel) if gas is not None else None
    out["nearby"] = near
    sufficient = near is not None and near["n_tests"] >= NEAR_MIN_TESTS and near["n_days"] >= NEAR_MIN_DAYS
    out["coverage"] = "sufficient" if sufficient else "limited" if near and near["n_tests"] else "none"
    if gravity != "microgravity":
        out["gravity_effect"] = {"tier": "C", "note": (
            "This atmosphere is evaluated in microgravity. The analyzed tests do not establish "
            "how flame persistence changes at the selected gravity.")}
    if fuel not in FUELS:
        out |= {"tier": "C", "tier_label": "No evidence", "reason": f"fuel '{fuel}' not tested in CFI-G (ethane, propane, butane)",
                "prediction": None, "caveats": caveats}
        return out
    f = source_features(xo2, p_kpa, fuel, x_fuel, m_fuel_mg_s)
    dom = artifact["domain"]
    in_range = {k: bool(dom["min"][k] <= f[k] <= dom["max"][k]) for k in PHYSICAL}
    z = np.array([(f[k] - dom["mean"][k]) / dom["sd"][k] for k in PHYSICAL])
    train_z = np.asarray(dom["train_z"])
    d5 = float(np.sort(np.sqrt(((train_z - z) ** 2).sum(axis=1)))[4])
    ratio = d5 / dom["typical_5th_nn_distance"]
    out["physics"] = {"tad_k": round(f["tad_k"], 1), "zst": round(f["zst"], 4), "m_tot_mg_s": round(f["m_tot_mg_s"], 4)}
    out["support"] = {"inside_tested_range": in_range, "distance_ratio_to_training": round(ratio, 2)}
    if not all(in_range.values()) or ratio > MAX_DISTANCE_RATIO:
        out |= {"tier": "A" if sufficient else "C", "tier_label": "Measured nearby" if sufficient else "No model reading",
                "prediction": None, "caveats": caveats,
                "reason": "outside the tested range of the physical inputs or too far from any tested flame"}
        return out
    tier, tier_label = ("A", "Measured nearby") if sufficient else ("B", "Model interpolation")
    if not sufficient:
        caveats.insert(0, "Nearby tests do not meet the coverage threshold." if near and near["n_tests"] else
                       "There are no tests in the selected atmosphere window.")
    x = np.array([f[k] for k in FEATURES])
    theta = np.asarray(artifact["theta"])
    draws = np.asarray(artifact["bootstrap_draws"])
    med = np.array([_predict(t, x) for t in draws])
    pred = {"median_burn_s": round(float(_predict(theta, x)), 1),
            "median_burn_s_90ci": [round(float(np.quantile(med, 0.05)), 1), round(float(np.quantile(med, 0.95)), 1)]}
    for t in (30.0, 60.0):
        s = np.array([_predict(th, x, t) for th in draws])
        pred[f"p_still_burning_{int(t)}s"] = round(float(_predict(theta, x, t)), 3)
        pred[f"p_still_burning_{int(t)}s_90ci"] = [round(float(np.quantile(s, 0.05)), 3), round(float(np.quantile(s, 0.95)), 3)]
    out |= {"tier": tier, "tier_label": tier_label, "prediction": pred, "caveats": caveats}
    return out


def reference_readings(artifact: dict, gas: pd.DataFrame, source: dict | None = None) -> list[dict]:
    """Readings for the reference cabin atmospheres (docs/04_physics/HABITAT_ATMOSPHERES.md)."""
    from flamesafe.physics.atmospheres import REFERENCE_ATMOSPHERES

    src = {**DEFAULT_SOURCE, **(source or {})}
    gravity_of = {0.0: "microgravity", 0.165: "moon", 0.38: "mars", 1.0: "earth"}
    out = []
    for key, a in REFERENCE_ATMOSPHERES.items():
        r = read(artifact, a.o2_mole_fraction, a.total_pressure_kpa, gas, src["fuel"], src["x_fuel"], src["m_fuel_mg_s"],
                 gravity=gravity_of.get(a.gravity_g, "microgravity"), label=a.name)
        out.append({"key": key, "gravity_g": a.gravity_g, **r})
    return out
