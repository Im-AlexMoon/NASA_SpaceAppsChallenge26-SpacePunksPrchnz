"""Descriptive categorical/numeric comparisons within explicit experimental blocks.

No tests, confidence intervals, imputation or predictive fitting are performed.
Cliff's delta is oriented as category A minus category B. Repeated experiments
are retained; per-operation medians expose the weighting of operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd

from flamesafe.analysis.segmentation import FAMILY_COLUMNS

MISSING_CATEGORY = "<sin_categoria>"
PRIMARY_VARIABLES = {
    "normal": ["xo2", "p_kpa", "x_fuel", "m_fuel_mg_s"],
    "inverse": ["xo2", "p_kpa", "x_fuel", "m_o2_mg_s"],
}
UNITS = {
    "xo2": "fracción molar", "x_fuel": "fracción molar", "p_kpa": "kPa",
    "m_fuel_mg_s": "mg/s", "m_o2_mg_s": "mg/s", "m_n2_mg_s": "mg/s",
    "po2_kpa": "kPa (derivada)", "zst": "fracción calculada",
    "tad_k": "K (calculada)", "burn_time_s": "s", "peak_burner_t_k": "K",
}
ORDERS = {
    "fuel": ["butane", "ethane", "propane", "ethylene"],
    "ignition_outcome": ["yes", "no", "flash"],
    "extinction_mode": ["self_extinguished", "flow_terminated"],
    "dilution_group": ["botella_30pct", "botella_50pct", "botella_100pct", "no_informada"],
}
COLORS = {
    "yes": "#2878B5", "no": "#D55E00", "flash": "#E8B339",
    "butane": "#D55E00", "ethane": "#009E73", "propane": "#9A60B4", "ethylene": "#2878B5",
    "botella_30pct": "#2878B5", "botella_50pct": "#E69F00", "botella_100pct": "#009E73",
    "no_informada": "#999999", "self_extinguished": "#009E73", "flow_terminated": "#CC79A7",
    MISSING_CATEGORY: "#999999",
}


@dataclass
class CategoricalDescription:
    summary: pd.DataFrame
    effects: pd.DataFrame
    operation_medians: pd.DataFrame
    panel_catalog: pd.DataFrame
    panels: dict[str, pd.DataFrame]


def cliffs_delta(a, b) -> float:
    """P(A > B) - P(A < B), ignoring nonfinite observations and counting ties as zero."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    a, b = a[np.isfinite(a)], np.sort(b[np.isfinite(b)])
    if not len(a) or not len(b):
        return np.nan
    less = np.searchsorted(b, a, side="left").sum()
    greater = (len(b) - np.searchsorted(b, a, side="right")).sum()
    return float((less - greater) / (len(a) * len(b)))


def category_order(category: str, present) -> list[str]:
    values = set(present)
    preferred = ORDERS.get(category, [])
    return [v for v in preferred if v in values] + sorted(values - set(preferred))


def _category_values(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna(MISSING_CATEGORY)


def describe_categories(
    data: pd.DataFrame,
    category: str,
    *,
    name: str,
    scenario: str = "principal",
    numeric_columns: list[str] | None = None,
    block_columns: list[str] | None = None,
    expected_levels: list[str] | None = None,
    min_effect_n: int = 5,
) -> CategoricalDescription:
    """Summarize each category without mixing the remaining family factors.

    The category being compared is removed from FAMILY_COLUMNS, not kept fixed.
    Geometry and campaign must always be fixed; each input must have unique trial
    identities. Null categories are reported but excluded from effects and plots.
    Missing categories expected by a protocol get explicit n=0 summary rows.
    """
    if data.duplicated(["psi_id", "test_id"]).any():
        raise ValueError("Comparisons require unique psi_id/test_id identities")
    if category in {"campaign", "flame_type", "period_group", "protocol_group", "outcome_source"}:
        raise ValueError("Provenance/geometry comparisons require separate coverage panels")
    if block_columns is None:
        block_columns = [c for c in FAMILY_COLUMNS if c != category]
    if category in block_columns or not {"campaign", "flame_type"} <= set(block_columns):
        raise ValueError("Hold campaign/geometry fixed and remove the comparison category from the block")
    missing = set([category, *block_columns, "operation_group"]) - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if data["operation_group"].isna().any():
        raise ValueError("Every trial requires an operation_group; do not silently lose operations")

    summary, effects, operations, catalog, panels = [], [], [], [], {}
    for block_no, (key, g) in enumerate(data.groupby(block_columns, dropna=False, sort=True), 1):
        key = key if isinstance(key, tuple) else (key,)
        block_label = " | ".join(f"{k}={v}" for k, v in zip(block_columns, key, strict=True))
        block_id = f"{name}:B{block_no:03d}"
        columns = numeric_columns if numeric_columns is not None else PRIMARY_VARIABLES[g["flame_type"].iloc[0]]
        actual_categories = _category_values(g[category])
        present = actual_categories.unique().tolist()
        levels = category_order(category, set(present) | set(expected_levels or []))
        fixed = dict(zip(block_columns, key, strict=True))
        for variable in columns:
            # Nitrogen feed is not recorded for CFI-G and flows have geometry-specific meaning.
            if variable == "m_n2_mg_s" and g["campaign"].iloc[0] != "Flame Design":
                continue
            if variable == "m_fuel_mg_s" and g["flame_type"].iloc[0] != "normal":
                continue
            if variable == "m_o2_mg_s" and g["flame_type"].iloc[0] != "inverse":
                continue
            values = pd.to_numeric(g[variable], errors="raise").astype(float).replace([np.inf, -np.inf], np.nan)
            panel_id = f"{scenario}:{block_id}:{variable}"
            base = {
                "analysis": name, "scenario": scenario, "block_id": block_id,
                "block_label": block_label, "panel_id": panel_id, "category": category,
                "variable": variable, "unit": UNITS.get(variable, ""), **fixed,
            }
            points = g[["psi_id", "test_id", "operation_group", "timestamp_verified"]].copy()
            points["category_level"] = actual_categories
            points["value"] = values
            panels[panel_id] = points
            observed_valid = points.loc[points["value"].notna() & points["category_level"].ne(MISSING_CATEGORY)]
            n_levels = observed_valid["category_level"].nunique()
            catalog.append({
                **base, "n_total": len(g), "n_valid": len(observed_valid),
                "n_operations": g["operation_group"].nunique(), "n_levels_valid": n_levels,
                "status": "comparable_descriptively" if n_levels >= 2 else "single_or_missing_category",
            })
            by_level = {}
            for level in levels:
                mask = actual_categories.eq(level)
                valid_mask = mask & values.notna()
                v = values.loc[valid_mask]
                op = g.loc[valid_mask].assign(_value=v).groupby("operation_group")["_value"].agg(["median", "size"])
                for operation, row in op.iterrows():
                    operations.append({**base, "category_level": level, "operation_group": operation,
                                       "n_valid": int(row["size"]), "operation_median": row["median"]})
                summary.append({
                    **base, "category_level": level, "category_missing": level == MISSING_CATEGORY,
                    "n_total": int(mask.sum()), "n_valid": len(v), "n_missing": int((mask & values.isna()).sum()),
                    "n_operations_total": g.loc[mask, "operation_group"].nunique(),
                    "n_operations_valid": len(op), "n_unique_values": v.nunique(),
                    "missing_pct": 100 * values.loc[mask].isna().mean() if mask.any() else np.nan,
                    "min": v.min(), "q25": v.quantile(0.25), "median": v.median(),
                    "q75": v.quantile(0.75), "max": v.max(),
                    "median_of_operation_medians": op["median"].median(),
                    "largest_operation_share": op["size"].max() / len(v) if len(v) else np.nan,
                    "status": "absent" if not mask.any() else "all_missing" if not len(v) else "observed",
                })
                if level != MISSING_CATEGORY and len(v):
                    by_level[level] = (v, len(op))
            for a, b in combinations(by_level, 2):
                va, opa = by_level[a]
                vb, opb = by_level[b]
                operations_a = set(points.loc[points["category_level"].eq(a) & points["value"].notna(), "operation_group"])
                operations_b = set(points.loc[points["category_level"].eq(b) & points["value"].notna(), "operation_group"])
                shared_operations = len(operations_a & operations_b)
                enough = min(len(va), len(vb)) >= min_effect_n
                low, high = max(va.min(), vb.min()), min(va.max(), vb.max())
                overlap = low <= high
                effects.append({
                    **base, "category_a": a, "category_b": b,
                    "n_a": len(va), "n_b": len(vb), "operations_a": opa, "operations_b": opb,
                    "n_shared_operations": shared_operations, "operations_disjoint": shared_operations == 0,
                    "median_difference_a_minus_b": va.median() - vb.median() if enough else np.nan,
                    "cliffs_delta_a_minus_b": cliffs_delta(va, vb) if enough else np.nan,
                    "effect_status": "descriptive_only" if enough else "fewer_than_5_values_per_category",
                    "single_operation_category": min(opa, opb) <= 1,
                    "univariate_ranges_overlap": bool(overlap),
                    "overlap_low": low if overlap else np.nan, "overlap_high": high if overlap else np.nan,
                    "n_a_in_overlap": int(va.between(low, high).sum()) if overlap else 0,
                    "n_b_in_overlap": int(vb.between(low, high).sum()) if overlap else 0,
                })
    return CategoricalDescription(
        summary=pd.DataFrame(summary), effects=pd.DataFrame(effects),
        operation_medians=pd.DataFrame(operations), panel_catalog=pd.DataFrame(catalog), panels=panels,
    )


def plot_comparison(description: CategoricalDescription, panel_id: str):
    """Return point/box/violin and ECDF panels with a visible operation overlay."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    s = description.summary.loc[description.summary["panel_id"].eq(panel_id)]
    meta = description.panel_catalog.set_index("panel_id").loc[panel_id]
    p = description.panels[panel_id]
    p = p.loc[p["value"].notna() & p["category_level"].ne(MISSING_CATEGORY)].copy()
    order = category_order(meta["category"], p["category_level"].unique())
    palette = {level: COLORS.get(level, "#666666") for level in order}
    fig, (ax, ecdf) = plt.subplots(1, 2, figsize=(12, 4.8), layout="constrained")
    if not len(p):
        ax.text(0.5, 0.5, "Sin valores disponibles", transform=ax.transAxes, ha="center")
        ecdf.set_visible(False)
        return fig
    for i, level in enumerate(order):
        subset = p.loc[p["category_level"].eq(level)]
        v = subset["value"].to_numpy()
        # Render eligible categories separately: sparse groups never get a smoothed violin.
        if len(v) >= 20 and len(np.unique(v)) >= 5:
            sns.violinplot(data=subset, x="category_level", y="value", order=order, color=palette[level],
                           inner=None, cut=0, linewidth=0.8, ax=ax)
        if len(v) >= 5:
            ax.boxplot([v], positions=[i], widths=0.18, showfliers=False, patch_artist=True,
                       boxprops={"facecolor": "white", "alpha": 0.8}, medianprops={"color": "black"},
                       manage_ticks=False)
        # Fixed jitter: the seed and sort keep repeat runs identical.
        rng = np.random.default_rng(42)
        ax.scatter(i + rng.uniform(-0.10, 0.10, len(v)), v, color=palette[level], alpha=0.45, s=13, zorder=3)
        op = description.operation_medians
        op = op.loc[op["panel_id"].eq(panel_id) & op["category_level"].eq(level)]
        offsets = np.linspace(-0.12, 0.12, len(op)) if len(op) > 1 else np.zeros(len(op))
        ax.scatter(i + offsets, op["operation_median"], marker="D", facecolors="none",
                   edgecolors="black", s=42, zorder=4, label="Mediana por operación" if i == 0 else None)
        sorted_v = np.sort(v)
        ecdf.step(sorted_v, np.arange(1, len(v) + 1) / len(v), where="post", color=palette[level],
                  label=f"{level}: n={len(v)}, operaciones={len(op)}")
        if len(v) == 1:
            ecdf.plot(sorted_v, [1], "o", color=palette[level])
    labels = []
    for level in order:
        row = s.loc[s["category_level"].eq(level)].iloc[0]
        labels.append(f"{level}\nn={row.n_valid}/{row.n_total}; ops={row.n_operations_valid}")
    absent = s.loc[s["status"].eq("absent"), "category_level"].tolist()
    ax.set_xticks(range(len(order)), labels, rotation=15, ha="right")
    ax.set(xlabel=meta["category"], ylabel=f"{meta['variable']} [{meta['unit']}]", title="Pruebas y medianas por operación")
    ax.legend(fontsize=8)
    ecdf.set(xlabel=f"{meta['variable']} [{meta['unit']}]", ylabel="Fracción acumulada", ylim=(0, 1.05),
             title="Distribuciones empíricas, sin imputación")
    ecdf.legend(fontsize=8)
    block_lines = meta["block_label"].split(" | ")
    title = f"{meta['block_id']} · {meta['variable']} · {meta['scenario']}\n"
    title += " | ".join(block_lines[:3]) + "\n" + " | ".join(block_lines[3:])
    if absent:
        title += "\nCategorías ausentes: " + ", ".join(absent)
    fig.suptitle(title, fontsize=10)
    return fig
