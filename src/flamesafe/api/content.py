"""Scientific content served by the API: MCDA ranking, M-01 v2 atmosphere readings and reviewed findings.

All three read the same evidence snapshot as the RAG (query_snapshot.duckdb) and obey configs/publication.yaml (ADR-0007).
"""

from __future__ import annotations

import threading
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import yaml
from pydantic import Field

from flamesafe import config
from flamesafe.rag.schemas import Contract


class RankingRequest(Contract):
    profile: str | None = Field(default=None, max_length=60)
    weights: dict[str, float] | None = None
    environment: str | None = Field(default=None, max_length=20)


class AtmosphereRequest(Contract):
    xo2: float = Field(gt=0, le=1, description="O2 mole fraction of the cabin atmosphere")
    p_kpa: float = Field(gt=0, le=1000, description="Total pressure, kPa")
    fuel: str = Field(default="propane", max_length=20)
    x_fuel: float = Field(default=0.3, gt=0, le=1, description="Fuel mole fraction of the burner stream (rest N2)")
    m_fuel_mg_s: float = Field(default=1.0, gt=0, le=20, description="Fuel mass flow, mg/s")
    gravity: str = Field(default="microgravity", max_length=20)


def publication() -> dict:
    return config.load("publication")["blocks"]


def _clean(value):
    """JSON-safe: NaN/inf -> None, numpy scalars -> Python."""
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


class ContentService:
    """Caches the snapshot tables per build and the model artifact."""

    def __init__(self, bundle: Path):
        self.bundle = bundle
        self._lock = threading.Lock()
        self._tables: dict[str, pd.DataFrame] = {}
        self._artifact = None

    def table(self, name: str) -> pd.DataFrame:
        with self._lock:
            if name not in self._tables:
                with duckdb.connect(str(self.bundle / "query_snapshot.duckdb"), read_only=True) as con:
                    self._tables[name] = con.sql(f"SELECT * FROM {name}").df()  # name from a fixed allowlist below
            return self._tables[name]

    def artifact(self) -> dict:
        from flamesafe.models import readings

        with self._lock:
            if self._artifact is None:
                self._artifact = readings.load()
            return self._artifact

    # ------------------------------------------------------------------ ranking
    def ranking_profiles(self) -> dict:
        cfg = config.load("ranking")
        return {"dimensions": cfg["dimensions"],
                "profiles": {k: {"label": v["label"], "environment": v["environment"], "weights": v["weights"]}
                             for k, v in cfg["profiles"].items()},
                "status": publication()["ranking"]["status"]}

    def ranking(self, req: RankingRequest) -> dict:
        from flamesafe.ranking import mcda

        inv = self.table("investigations")
        r = mcda.rank(inv, req.profile, weights=req.weights, environment=req.environment)
        sens = mcda.sensitivity(inv, r.profile) if req.weights is None and req.environment is None else None
        cols = ["rank", "psi_id", "acronym", "title", "tier", "access_status", "n_gold_tests", "score",
                *mcda.DIMENSIONS, *[f"contrib_{d}" for d in mcda.DIMENSIONS]]
        return _clean({
            "profile": r.profile, "environment": r.environment, "weights": r.weights,
            "rows": r.table[cols].round(4).replace({np.nan: None}).to_dict("records"),
            "sensitivity": None if sens is None else {
                "perturbation": config.load("ranking")["sensitivity"]["perturbation"],
                "top_k": config.load("ranking")["sensitivity"]["top_k"],
                "perturbations_changing_top_k": int((sens.top_k_changed > 0).sum()), "n_perturbations": len(sens),
                "max_changed": int(sens.top_k_changed.max())},
            "status": publication()["ranking"]["status"],
            "method": "docs/03_data_science/RANKING_METHODOLOGY.md"})

    # ------------------------------------------------------------------ readings
    def reference_readings(self) -> dict:
        from flamesafe.models import readings

        art = self.artifact()
        return _clean({"model_id": art["model_id"], "review": art["review"], "metrics": art["metrics"],
                       "status": publication()["model_readings"]["status"],
                       "readings": readings.reference_readings(art, self.table("gas_flame_tests"))})

    def reading(self, req: AtmosphereRequest) -> dict:
        from flamesafe.models import readings

        r = readings.read(self.artifact(), req.xo2, req.p_kpa, self.table("gas_flame_tests"), req.fuel, req.x_fuel,
                          req.m_fuel_mg_s, req.gravity)
        return _clean({**r, "status": publication()["model_readings"]["status"]})

    # ------------------------------------------------------------------ findings
    @staticmethod
    def findings() -> dict:
        path = config.ROOT / publication()["findings"]["source"]
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return {"status": publication()["findings"]["status"], **data}
