"""Guard against deleting real replicas or multiplying tests in temporal joins."""

import pandas as pd

from flamesafe.analysis.segmentation import audit_gas_observations, condition_candidates


def fixture_frames():
    gas = pd.DataFrame([{
        "psi_id": "PSI-159", "campaign": "CFI-G", "test_id": test,
        "test_day": 1, "flame_type": "normal", "fuel": "propane",
        "fuel_dilution_pct": 30.0, "qualifier": None,
        "outcome_source": "experimental_table", "ignited": True,
        "ignition_outcome": "yes", "xo2": 0.21, "p_kpa": 100.0,
        "x_fuel": 0.3, "m_fuel_mg_s": 1.0, "m_o2_mg_s": float("nan"),
        "source_file": "source.csv", "source_row": i + 2,
    } for i, test in enumerate(["21088A1", "21088A2"])])
    events = pd.DataFrame([{
        "psi_id": "PSI-159", "tpid": test, "op": "TP", "ignite": True,
        "t_start_gmt": f"2021-03-29 {hour}:00:00",
        "t_end_gmt": f"2021-03-29 {hour}:01:00",
        "source_file": "events.xlsx", "source_row": i + 5,
    } for i, (test, hour) in enumerate([("21088A1", "12"), ("21088A2", "13")])])
    return gas, events


def test_same_date_and_same_settings_do_not_delete_distinct_trials():
    gas, events = fixture_frames()
    result = audit_gas_observations(gas, events)
    assert len(result.unique) == 2
    assert result.observations.audit_ok.all()
    assert result.unique.utc_date.nunique() == 1
    assert len(condition_candidates(result.unique)) == 2
    assert result.unique.operation_group.nunique() == 1


def test_only_identical_copies_of_the_same_key_are_removed():
    gas, events = fixture_frames()
    duplicate = gas.iloc[[0]].assign(source_file="copy.csv", source_row=55)
    result = audit_gas_observations(pd.concat([gas, duplicate]), events)
    assert len(result.unique) == 2
    assert len(result.removed_copies) == 1
    assert result.identity_conflicts.empty


def test_conflicting_key_is_quarantined_instead_of_selecting_first():
    gas, events = fixture_frames()
    conflict = gas.iloc[[0]].assign(ignited=False, ignition_outcome="no")
    result = audit_gas_observations(pd.concat([gas, conflict]), events)
    assert len(result.identity_conflicts) == 2
    assert len(result.unique) == 1
    assert result.observations.audit_ok.sum() == 1


def test_ambiguous_event_join_never_multiplies_or_silently_selects_dates():
    gas, events = fixture_frames()
    conflict = events.iloc[[0]].assign(t_start_gmt="2021-03-29 11:00:00")
    result = audit_gas_observations(gas, pd.concat([events, conflict]))
    assert len(result.observations) == 2
    assert len(result.event_conflicts) == 2
    ambiguous = result.observations.set_index("test_id").loc["21088A1"]
    assert ambiguous.event_identity_conflict
    assert pd.isna(ambiguous.t_start_gmt)
    assert not ambiguous.audit_ok


def test_missing_dates_remain_missing_and_cross_midnight_trials_share_block():
    gas, events = fixture_frames()
    events.loc[1, ["t_start_gmt", "t_end_gmt"]] = ["2021-03-30 00:01:00", "2021-03-30 00:02:00"]
    result = audit_gas_observations(gas, events)
    assert result.unique.utc_date.nunique() == 2
    assert result.unique.operation_group.nunique() == 1
    missing = audit_gas_observations(gas, events.iloc[[0]])
    row = missing.unique.set_index("test_id").loc["21088A2"]
    assert pd.isna(row.t_start_gmt)
    assert row.period_group == "sin_fecha"
    assert not row.timestamp_verified
    assert row.audit_ok  # absence is not evidence of duplication


def test_bad_duration_and_zero_flow_controls_are_explicit():
    gas, events = fixture_frames()
    events.loc[0, "t_end_gmt"] = "2021-03-28 12:01:00"
    gas.loc[1, ["m_fuel_mg_s", "x_fuel"]] = 0.0
    result = audit_gas_observations(gas, events)
    assert result.observations.negative_event_duration.sum() == 1
    assert result.observations.audit_ok.sum() == 1
    assert result.observations.protocol_group.eq("control_flujo_cero").sum() == 1
    assert not result.observations.is_cfig_binary.any()
