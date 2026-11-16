"""Static content snapshot for the web app (ADR-0011).

Writes the reviewed scientific content to JSON files that the Next.js app bundles at build time, so the public
dashboard on Vercel works without a running backend. Every value comes from the same functions the API serves
(`ContentService`, `readings.read`, `mcda.dimension_scores`); nothing is computed differently here.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import yaml

from flamesafe import config
from flamesafe.api.content import ContentService, _clean, publication
from flamesafe.models import readings
from flamesafe.pipeline.promotion import promote_files, stage_files
from flamesafe.rag.utils import file_hash
from flamesafe.ranking import mcda

# Slider grid of the Atmosphere Explorer: O2 mole fraction x total pressure (microgravity, default CFI-G burner stream).
GRID_XO2 = [round(x, 2) for x in np.arange(0.14, 0.501, 0.01)]
GRID_P_KPA = [30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 56.5, 60.0, 65.0, 70.3, 75.0, 80.0, 85.0, 90.0, 95.0, 101.3]
TEST_COLUMNS = ["psi_id", "campaign", "test_id", "test_day", "flame_type", "fuel", "xo2", "p_kpa", "ignition_outcome",
                "extinction_mode", "burn_time_s", "cool_flame", "source_file", "source_row", "outcome_source"]


def _write(out: Path, name: str, data) -> int:
    path = out / f"{name}.json"
    text = json.dumps(_clean(data), ensure_ascii=False, separators=(",", ":"))
    path.write_text(text + "\n", encoding="utf-8", newline="\n")
    return len(text)


def _grid_point(r: dict) -> dict:
    p = r["prediction"] or {}
    near = {key: value for key, value in r["nearby"].items() if key != "tests"}
    return {"tier": r["tier"], "coverage": r["coverage"], "nearby": near, "reason": r.get("reason"), "median": p.get("median_burn_s"), "ci": p.get("median_burn_s_90ci"),
            "p30": p.get("p_still_burning_30s"), "p60": p.get("p_still_burning_60s"),
            "p30_ci": p.get("p_still_burning_30s_90ci"), "p60_ci": p.get("p_still_burning_60s_90ci"),
            "n_near": r["nearby"]["n_tests"], "obs_median": r["nearby"]["median_burn_s_self_extinguished"],
            "tad": r["physics"]["tad_k"], "dist": r["support"]["distance_ratio_to_training"]}


def export(out: Path, bundle: Path) -> dict[str, int]:
    out.mkdir(parents=True, exist_ok=True)
    with stage_files(out.parent, "web-content") as stage:
        result = _export(stage, bundle)
        promote_files(stage, out)
        return result


def _export(out: Path, bundle: Path) -> dict[str, int]:
    svc = ContentService(bundle)
    policy = publication()
    art = svc.artifact() if policy["model_readings"]["enabled"] else None
    gas = svc.table("gas_flame_tests")
    inv = svc.table("investigations")
    sizes: dict[str, int] = {}

    sizes["findings"] = _write(out, "findings", svc.findings() if policy["findings"]["enabled"] else {"findings": []})

    if policy["ranking"]["enabled"]:
        cfg = config.load("ranking")
        dims = {env: mcda.dimension_scores(inv, env, cfg).to_dict("records")
                for env in mcda.ENVIRONMENTS}
        sens = {}
        for name in cfg["profiles"]:
            s = mcda.sensitivity(inv, name, cfg)
            sens[name] = {"n_perturbations": len(s), "perturbations_changing_top_k": int((s.top_k_changed > 0).sum()),
                          "max_changed": int(s.top_k_changed.max()), "joint": mcda.joint_sensitivity(inv, name, cfg)}
        sizes["ranking"] = _write(out, "ranking", {
            "status": publication()["ranking"]["status"], "dimensions": cfg["dimensions"],
            "dimension_order": list(mcda.DIMENSIONS), "environments": list(mcda.ENVIRONMENTS),
            "profiles": {k: {"label": v["label"], "environment": v["environment"], "weights": v["weights"]}
                         for k, v in cfg["profiles"].items()},
            "sensitivity": {**cfg["sensitivity"], "by_profile": sens},
            "investigations": inv[["psi_id", "acronym", "title", "tier", "access_status", "n_gold_tests", "hardware_family", "flight_platform", "doi"]]
            .replace({np.nan: None}).to_dict("records"),
            "scores": dims, "formula": "score = sum(w_d * s_d) / sum(w_d)",
            "method": "docs/03_data_science/RANKING_METHODOLOGY.md"})
    else:
        sizes["ranking"] = _write(out, "ranking", {"investigations": [], "profiles": {}})

    if art is not None:
        ref = svc.reference_readings()
        grid = [[_grid_point(readings.read(art, x, p, gas)) for x in GRID_XO2] for p in GRID_P_KPA]
        sizes["readings"] = _write(out, "readings", {
            "model_id": art["model_id"], "review": art["review"], "metrics": art["metrics"],
            "status": publication()["model_readings"]["status"], "source": readings.DEFAULT_SOURCE,
            "references": ref["readings"],
            "grid": {"xo2": GRID_XO2, "p_kpa": GRID_P_KPA, "gravity": "microgravity", "points": grid}})
    else:
        sizes["readings"] = _write(out, "readings", {"references": [], "grid": {"xo2": [], "p_kpa": [], "points": []}})

    tests = gas[TEST_COLUMNS].copy()
    tests["burn_time_s"] = tests["burn_time_s"].where(tests["ignition_outcome"] == "yes")
    sizes["tests"] = _write(out, "tests", {
        "columns": TEST_COLUMNS, "n": len(tests),
        "rows": tests.replace({np.nan: None}).round(4).values.tolist()})

    curated = yaml.safe_load((config.ROOT / "configs" / "dashboard_evidence.yaml").read_text(encoding="utf-8"))
    sizes["dashboard"] = _write(out, "dashboard", {
        **curated,
        "model": {key: art[key] for key in ("model_id", "metrics", "coef_table", "cohort")} if art else None})

    sizes["meta"] = _write(out, "meta", {
        "schema_version": 2, "build_id": bundle.name, "model_id": art["model_id"] if art else None,
        "publication": policy, "hashes": {key: file_hash(config.ROOT / policy[key]["source"])
                                             for key in policy if policy[key]["enabled"]},
        "counts": {"investigations": len(inv), "gas_flame_tests": len(gas),
                   "gas_ignited": int((gas["ignition_outcome"] == "yes").sum()),
                   "model_cohort": art["cohort"]["n"] if art else None, "model_days": art["cohort"]["days"] if art else None}})
    return sizes
