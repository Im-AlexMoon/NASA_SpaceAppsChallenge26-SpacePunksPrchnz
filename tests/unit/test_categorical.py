"""Scientific safeguards for descriptive comparisons, sparse groups and regeneration."""

import copy

import numpy as np
import pandas as pd
import pytest

from flamesafe.analysis.categorical import cliffs_delta, describe_categories
from flamesafe.analysis.notebook_sections import replace_section


def trials():
    rows = []
    for fuel in ["butane", "propane"]:
        for i in range(6):
            rows.append({
                "psi_id": "PSI-159", "test_id": f"{fuel}{i}", "campaign": "CFI-G",
                "flame_type": "normal", "fuel": fuel, "dilution_group": "botella_30pct",
                "period_group": "2021", "protocol_group": "sin_anotacion",
                "outcome_source": "experimental_table", "ignition_outcome": "yes" if i else "no",
                "operation_group": f"{fuel}-op{int(i > 0)}", "timestamp_verified": True,
                "xo2": 0.3 if fuel == "butane" else 0.2, "p_kpa": 100.0,
                "x_fuel": np.nan if i == 0 else 0.3, "m_fuel_mg_s": 1.0,
                "m_o2_mg_s": np.nan, "m_n2_mg_s": np.nan,
            })
    return pd.DataFrame(rows)


def test_compared_factor_varies_but_campaign_and_geometry_never_mix():
    data = trials()
    other = data.assign(psi_id="PSI-10", campaign="Flame Design")
    data = pd.concat([data, other], ignore_index=True)
    result = describe_categories(data, "fuel", name="fuel")
    assert result.panel_catalog.block_id.nunique() == 2
    assert result.effects.loc[result.effects.variable.eq("xo2"), "cliffs_delta_a_minus_b"].eq(1).all()
    assert set(result.summary.campaign) == {"CFI-G", "Flame Design"}
    assert not result.summary.variable.eq("m_o2_mg_s").any()
    assert result.summary.query("variable == 'x_fuel'").n_missing.eq(1).all()
    with pytest.raises(ValueError, match="Provenance"):
        describe_categories(data, "campaign", name="bad")


def test_effect_orientation_ties_and_constant_categories():
    assert cliffs_delta([3, 3], [1, 1]) == 1
    assert cliffs_delta([1, 1], [3, 3]) == -1
    assert cliffs_delta([1, 1], [1, 1]) == 0
    assert cliffs_delta([1, 2, np.nan], [1, 2, np.inf]) == 0
    result = describe_categories(trials(), "fuel", name="fuel")
    constant = result.effects.loc[result.effects.variable.eq("p_kpa")].iloc[0]
    assert constant.cliffs_delta_a_minus_b == 0
    assert constant.univariate_ranges_overlap


def test_sparse_and_absent_outcomes_are_reported_without_effect_estimates():
    data = trials()
    data.loc[0, "ignition_outcome"] = None
    result = describe_categories(data, "ignition_outcome", name="ignition", expected_levels=["yes", "no", "flash"])
    absent = result.summary[result.summary.category_level.eq("flash")]
    assert absent.n_total.eq(0).all()
    assert absent.status.eq("absent").all()
    assert result.summary.category_missing.any()
    assert result.effects.cliffs_delta_a_minus_b.isna().all()
    assert result.effects.effect_status.eq("fewer_than_5_values_per_category").all()


def test_operation_medians_and_counts_do_not_count_rows_as_independent_groups():
    data = trials()
    data.loc[data.fuel.eq("butane"), "xo2"] = [1, 10, 10, 10, 10, 10]
    result = describe_categories(data, "fuel", name="fuel")
    row = result.summary.query("variable == 'xo2' and category_level == 'butane'").iloc[0]
    assert row.n_total == 6 and row.n_operations_valid == 2
    assert row["median"] == 10
    assert row.median_of_operation_medians == 5.5
    assert result.effects.operations_disjoint.all()
    shared = data.copy()
    shared["operation_group"] = shared["operation_group"].str.replace(r"^[^-]+-", "", regex=True)
    shared_result = describe_categories(shared, "fuel", name="shared")
    shared_effects = shared_result.effects.set_index("variable")
    assert shared_effects.loc["xo2", "n_shared_operations"] == 2
    assert shared_effects.loc["x_fuel", "n_shared_operations"] == 1  # op0 has missing x_fuel
    assert not shared_result.effects.operations_disjoint.any()
    with pytest.raises(ValueError, match="unique"):
        describe_categories(pd.concat([data, data.iloc[[0]]]), "fuel", name="bad")


def test_empty_input_produces_no_comparisons():
    result = describe_categories(trials().iloc[:0], "fuel", name="empty")
    assert result.summary.empty and not result.panels


def test_nitrogen_is_not_imputed_into_cfig():
    result = describe_categories(trials(), "fuel", name="n2", numeric_columns=["m_n2_mg_s"])
    assert result.summary.empty
    assert not result.panels


def test_bounded_regeneration_preserves_trailing_analysis_and_fails_on_unknown_end():
    cells = [
        {"source": "original"},
        {"source": "<!-- FLAMESAFE:SEGMENTATION:BEGIN -->"},
        {"source": "legacy final: Tablas auditables:"},
        {"source": "categorical analysis"}, {"source": "user notes"},
    ]
    before = copy.deepcopy(cells)
    new = [{"source": "<!-- FLAMESAFE:SEGMENTATION:BEGIN -->\nnew\n<!-- FLAMESAFE:SEGMENTATION:END -->"}]
    result = replace_section(cells, "SEGMENTATION", new, legacy_end_token="Tablas auditables:")
    assert result[-2:] == cells[-2:]
    assert cells == before
    assert replace_section(result, "SEGMENTATION", new) == result
    with pytest.raises(ValueError, match="unique safe end"):
        replace_section(cells, "SEGMENTATION", new)
