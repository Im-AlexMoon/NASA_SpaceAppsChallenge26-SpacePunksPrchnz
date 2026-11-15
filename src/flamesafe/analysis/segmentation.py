"""Conservative identity, chronology and family audit for gas_flame_tests.

Dates alone and matching conditions never justify deleting an experiment.
Only identical copies of the same investigation/test are removed; conflicting
identities are retained in the audit and excluded from analytical cohorts.
These functions do not write to the medallion layers.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

KEY = ["psi_id", "test_id"]
PROVENANCE = {
    "source_file", "source_row", "source_sha256", "acronym", "tier",
    "hardware_family", "environments", "_input_row",
}
FAMILY_COLUMNS = [
    "campaign", "flame_type", "fuel", "dilution_group", "period_group",
    "protocol_group", "outcome_source",
]


@dataclass
class GasAudit:
    observations: pd.DataFrame
    unique: pd.DataFrame
    removed_copies: pd.DataFrame
    identity_conflicts: pd.DataFrame
    event_conflicts: pd.DataFrame
    temporal_collisions: pd.DataFrame
    summary: pd.DataFrame


def _normalize(values: pd.Series) -> pd.Series:
    return values.astype("string").str.replace(r"\s+", "", regex=True).str.upper()


def audit_gas_observations(gas: pd.DataFrame, events: pd.DataFrame) -> GasAudit:
    """Resolve identity before a many-to-one temporal join, with full audit trails.

    EventData dates are GMT/UTC. Ambiguous event keys are not resolved with
    drop_duplicates(keep='first'). Missing timestamps remain explicitly missing.
    """
    d = gas.copy().reset_index(drop=True)
    d["_input_row"] = np.arange(len(d))
    for col in KEY:
        d[col] = _normalize(d[col])
    invalid_key = d[KEY].isna().any(axis=1) | d[KEY].eq("").any(axis=1)
    payload = [c for c in gas.columns if c not in PROVENANCE]
    repeated = d.loc[~invalid_key & d.duplicated(KEY, keep=False)]
    conflicting_keys = (
        repeated.groupby(KEY, dropna=False)[payload].nunique(dropna=False)
        .gt(1).any(axis=1)
    )
    conflicting_keys = conflicting_keys[conflicting_keys].index
    key_index = pd.MultiIndex.from_frame(d[KEY])
    conflict = key_index.isin(conflicting_keys)
    copy_mask = d.duplicated(KEY, keep="first") & ~conflict & ~invalid_key
    d["identity_status"] = np.select(
        [invalid_key, conflict, copy_mask],
        ["missing_key", "conflicting_key", "identical_copy"],
        default="unique",
    )

    e = events.copy()
    e = e[e["op"].isin(["TP", "INV_TP"])].copy()
    e["psi_id"] = _normalize(e["psi_id"])
    e["test_id"] = _normalize(e["tpid"])
    for col in ["t_start_gmt", "t_end_gmt"]:
        e[col] = pd.to_datetime(e[col], errors="coerce", utc=True)
    e = e[e[KEY].notna().all(axis=1) & e[KEY].ne("").all(axis=1)].copy()
    event_payload = [c for c in e if c not in PROVENANCE]
    distinct_events = e.drop_duplicates(subset=event_payload)
    event_conflict_mask = distinct_events.duplicated(KEY, keep=False)
    event_conflicts = distinct_events.loc[event_conflict_mask].copy()
    bad_event_keys = pd.MultiIndex.from_frame(event_conflicts[KEY])
    d["event_identity_conflict"] = key_index.isin(bad_event_keys)
    lookup = distinct_events.loc[~event_conflict_mask, [
        *KEY, "op", "t_start_gmt", "t_end_gmt", "source_file", "source_row",
    ]].rename(columns={"source_file": "event_source_file", "source_row": "event_source_row"})
    d = d.merge(lookup, on=KEY, how="left", validate="many_to_one", sort=False)
    expected_op = d["flame_type"].map({"normal": "TP", "inverse": "INV_TP"})
    d["event_op_mismatch"] = d["op"].notna() & d["op"].ne(expected_op)
    d["utc_date"] = d["t_start_gmt"].dt.strftime("%Y-%m-%d")
    d["duration_event_s"] = (d["t_end_gmt"] - d["t_start_gmt"]).dt.total_seconds()
    d["negative_event_duration"] = d["duration_event_s"].lt(0)

    # Distinct IDs at exactly the same start time deserve inspection, not deletion.
    representatives = d[d["identity_status"].eq("unique") & d["t_start_gmt"].notna()]
    collisions = representatives.duplicated(["psi_id", "t_start_gmt"], keep=False)
    collision_rows = representatives.loc[collisions, "_input_row"]
    d["temporal_collision"] = d["_input_row"].isin(collision_rows)
    d["audit_ok"] = (
        d["identity_status"].eq("unique") & ~d["event_identity_conflict"]
        & ~d["event_op_mismatch"] & ~d["temporal_collision"] & ~d["negative_event_duration"]
    )
    d["timestamp_verified"] = d["audit_ok"] & d["t_start_gmt"].notna()

    # Identifier prefix is an operational block token, NOT an inferred UTC date.
    prefix = d["test_id"].str.extract(r"^(\d{5})", expand=False)
    fallback = "day=" + d["test_day"].astype("string")
    d["operation_group"] = (
        d["psi_id"] + "|" + d["flame_type"] + "|" + prefix.fillna(fallback)
    )
    d["series_id"] = d["psi_id"] + "|" + d["test_id"].str.replace(r"\d+$", "", regex=True)
    d["period_group"] = d["t_start_gmt"].dt.year.astype("Int64").astype("string").fillna("sin_fecha")
    d["dilution_group"] = d["fuel_dilution_pct"].map(
        lambda v: "no_informada" if pd.isna(v) else f"botella_{v:g}pct"
    )
    d["protocol_group"] = d["qualifier"].fillna("sin_anotacion").astype("string")
    zero_feed = (
        d["flame_type"].eq("normal") & (d["x_fuel"].eq(0) | d["m_fuel_mg_s"].eq(0))
    ) | (
        d["flame_type"].eq("inverse") & (d["xo2"].eq(0) | d["m_o2_mg_s"].eq(0))
    )
    d.loc[zero_feed, "protocol_group"] = "control_flujo_cero"
    d["family_base"] = d[["campaign", "flame_type", "fuel"]].astype("string").agg(" | ".join, axis=1)
    d["family_id"] = d[FAMILY_COLUMNS].astype("string").fillna("no_informado").agg(" | ".join, axis=1)
    d["is_cfig_binary"] = (
        d["audit_ok"] & d["campaign"].eq("CFI-G") & d["ignited"].notna()
        & d["outcome_source"].eq("experimental_table")
        & d["protocol_group"].eq("sin_anotacion")
    )

    unique = d.loc[d["identity_status"].eq("unique")].copy()
    counts = {
        "input_rows": len(d),
        "exact_rows_repeated_extra": int(gas.duplicated().sum()),
        "repeated_key_rows": int(d.duplicated(KEY, keep=False).sum()),
        "identical_copies_removed": int(copy_mask.sum()),
        "conflicting_key_rows": int(conflict.sum()),
        "missing_key_rows": int(invalid_key.sum()),
        "event_conflict_rows": len(event_conflicts),
        "temporal_collision_rows": int(d["temporal_collision"].sum()),
        "negative_event_duration_rows": int(d["negative_event_duration"].sum()),
        "event_op_mismatch_rows": int(d["event_op_mismatch"].sum()),
        "retained_unique_rows": len(unique),
        "audit_ok_rows": int(d["audit_ok"].sum()),
        "timestamp_verified_rows": int(d["timestamp_verified"].sum()),
        "unmatched_event_rows": int(d["op"].isna().sum()),
        "operation_groups": d.loc[d["audit_ok"], "operation_group"].nunique(),
        "strict_families": d.loc[d["audit_ok"], "family_id"].nunique(),
    }
    return GasAudit(
        observations=d,
        unique=unique,
        removed_copies=d.loc[d["identity_status"].eq("identical_copy")].copy(),
        identity_conflicts=d.loc[d["identity_status"].isin(["conflicting_key", "missing_key"])].copy(),
        event_conflicts=event_conflicts,
        temporal_collisions=d.loc[d["temporal_collision"]].copy(),
        summary=pd.Series(counts, name="n").rename_axis("check").to_frame(),
    )


def family_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Counts and descriptive label fractions; these are not independent trials."""
    rows = []
    for family, g in data.groupby("family_id", sort=True):
        labels = g["ignition_outcome"].value_counts()
        binary = g["ignited"].dropna()
        rows.append({
            "family_id": family, "n": len(g), "operation_groups": g["operation_group"].nunique(),
            "utc_dates": g["utc_date"].nunique(), "without_timestamp": int(g["t_start_gmt"].isna().sum()),
            "yes": int(labels.get("yes", 0)), "no": int(labels.get("no", 0)),
            "flash": int(labels.get("flash", 0)), "missing_label": int(g["ignition_outcome"].isna().sum()),
            "yes_pct_binary": 100 * binary.mean() if len(binary) else np.nan,
        })
    return pd.DataFrame(rows)


def condition_candidates(data: pd.DataFrame) -> pd.DataFrame:
    """Exact matching observed settings: candidates for replicas, never auto-delete.

    Missing settings are excluded, so two NaNs cannot establish equivalence.
    No rounding/tolerances are silently introduced. Unrecorded conditions may differ.
    """
    rows = []
    for family, g in data.groupby("family_id", sort=True):
        geometry = g["flame_type"].iloc[0]
        fields = ["xo2", "p_kpa", "x_fuel", "m_fuel_mg_s" if geometry == "normal" else "m_o2_mg_s"]
        if g["campaign"].iloc[0] == "Flame Design":
            fields.append("m_n2_mg_s")
        elif geometry == "inverse":
            fields.append("hc_burnrate_mg_s")
        complete = g.dropna(subset=fields)
        for settings, replicas in complete.groupby(fields, sort=True):
            if len(replicas) < 2:
                continue
            for _, r in replicas.iterrows():
                rows.append({
                    "family_id": family,
                    "settings": repr(dict(zip(fields, settings, strict=True))),
                    "psi_id": r["psi_id"], "test_id": r["test_id"],
                    "t_start_gmt": r["t_start_gmt"], "operation_group": r["operation_group"],
                    "ignition_outcome": r["ignition_outcome"], "source_file": r["source_file"],
                    "source_row": r["source_row"], "n_matching_settings": len(replicas),
                })
    return pd.DataFrame(rows, columns=[
        "family_id", "settings", "psi_id", "test_id", "t_start_gmt", "operation_group",
        "ignition_outcome", "source_file", "source_row", "n_matching_settings",
    ])
