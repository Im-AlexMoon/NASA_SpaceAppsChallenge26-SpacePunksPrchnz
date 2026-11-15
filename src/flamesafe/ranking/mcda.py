"""DS-07 · Transparent multi-criteria (MCDA) ranking of the PSI combustion investigations.

Each investigation gets seven dimension scores in [0, 1] computed from versioned inputs (triage tags and R1-R6 scores,
access status, publications with DOI). A profile is a set of weights plus a target environment; the score is the weighted
mean of the dimensions. Nothing is learned or hidden: every number can be traced to `configs/triage.yaml`,
`configs/ranking.yaml` and the gold `investigations` table, and users may supply their own weights.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from flamesafe import config

PILLARS = ("prevencion", "deteccion", "supresion")
ENVIRONMENTS = ("nave", "estacion", "base_lunar", "rover", "marte")
DIMENSIONS = ("pillar_prevencion", "pillar_deteccion", "pillar_supresion", "environment", "evidence", "modeling",
              "maturity")


def _split(value) -> list[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, (list, tuple, np.ndarray)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in str(value).split(",") if v.strip()]


def dimension_scores(investigations: pd.DataFrame, environment: str, cfg: dict | None = None) -> pd.DataFrame:
    """One row per investigation with the seven dimension scores for a target `environment`."""
    cfg = cfg or config.load("ranking")
    sc = cfg["scoring"]
    if environment not in ENVIRONMENTS:
        raise ValueError(f"unknown environment {environment!r}; expected one of {ENVIRONMENTS}")
    inv = investigations.copy()
    r = {k: inv[k].astype(float) / 3.0 for k in ("R1", "R2", "R3", "R4", "R5")}
    pubs = inv["n_publications_with_doi"].fillna(0).astype(float)
    out = pd.DataFrame({"psi_id": inv["psi_id"]})
    for pillar in PILLARS:
        factors = []
        for tags in inv["pillars"].map(_split):
            if pillar not in tags:
                factors.append(0.0)
            else:
                factors.append(sc["primary_pillar_factor"] if tags.index(pillar) == 0 else sc["secondary_pillar_factor"])
        out[f"pillar_{pillar}"] = np.array(factors) * r["R1"].to_numpy()
    in_env = inv["environments"].map(lambda v: environment in _split(v)).astype(float)
    ground = inv["is_ground_investigation"].fillna(False).astype(bool)
    out["environment"] = in_env * np.where(ground, sc["ground_investigation_environment_factor"], 1.0)
    access = inv["access_status"].map(sc["access_penalty"]).fillna(min(sc["access_penalty"].values()))
    out["evidence"] = (r["R2"] + r["R3"] + r["R5"]) / 3.0 * access
    out["modeling"] = r["R4"]
    out["maturity"] = np.log1p(pubs) / np.log1p(pubs.max()) if pubs.max() > 0 else 0.0
    return out


@dataclass
class Ranking:
    profile: str
    environment: str
    weights: dict[str, float]
    table: pd.DataFrame  # psi_id, acronym, title, score, rank, the seven dimensions and each dimension's contribution


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    unknown = set(weights) - set(DIMENSIONS)
    if unknown:
        raise ValueError(f"unknown dimensions: {sorted(unknown)}")
    w = {d: float(weights.get(d, 0.0)) for d in DIMENSIONS}
    if any(v < 0 for v in w.values()) or sum(w.values()) <= 0:
        raise ValueError("weights must be non-negative and not all zero")
    total = sum(w.values())
    return {d: v / total for d, v in w.items()}


def rank(investigations: pd.DataFrame, profile: str | None = None, weights: dict[str, float] | None = None,
         environment: str | None = None, cfg: dict | None = None) -> Ranking:
    """Rank with a named profile, or with custom `weights` (+ `environment`), which override the profile's."""
    cfg = cfg or config.load("ranking")
    prof = cfg["profiles"].get(profile or "student")
    if prof is None:
        raise ValueError(f"unknown profile {profile!r}; expected one of {sorted(cfg['profiles'])}")
    env = environment or prof["environment"]
    w = normalize_weights(weights or prof["weights"])
    dims = dimension_scores(investigations, env, cfg)
    contrib = pd.DataFrame({f"contrib_{d}": dims[d] * w[d] for d in DIMENSIONS})
    table = pd.concat([investigations[["psi_id", "acronym", "title", "tier", "access_status", "n_gold_tests"]]
                       .reset_index(drop=True), dims.drop(columns="psi_id").reset_index(drop=True), contrib], axis=1)
    table["score"] = contrib.sum(axis=1)
    table = table.sort_values(["score", "psi_id"], ascending=[False, True]).reset_index(drop=True)
    table["rank"] = np.arange(1, len(table) + 1)
    return Ranking(profile or "student", env, w, table)


def sensitivity(investigations: pd.DataFrame, profile: str, cfg: dict | None = None) -> pd.DataFrame:
    """Top-k stability: perturb one weight at a time by +/-p and count how many of the top-k change."""
    cfg = cfg or config.load("ranking")
    p, k = cfg["sensitivity"]["perturbation"], cfg["sensitivity"]["top_k"]
    base = rank(investigations, profile, cfg=cfg)
    base_top = list(base.table.psi_id.head(k))
    rows = []
    for d in DIMENSIONS:
        for sign in (-1, 1):
            w = dict(base.weights)
            w[d] = max(w[d] * (1 + sign * p), 0.0)
            top = list(rank(investigations, profile, weights=w, environment=base.environment, cfg=cfg).table.psi_id.head(k))
            rows.append({"dimension": d, "change": f"{'+' if sign > 0 else '-'}{int(p * 100)}%",
                         "top_k_changed": len(set(base_top) - set(top)), "same_order": top == base_top})
    return pd.DataFrame(rows)
