"""DS-07: MCDA ranking is transparent, bounded and respects the weights."""

from __future__ import annotations

import pandas as pd
import pytest

from flamesafe.ranking import mcda


@pytest.fixture
def inv():
    return pd.DataFrame([
        {"psi_id": "PSI-1", "acronym": "A", "title": "gas flames", "tier": 1, "access_status": "available",
         "n_gold_tests": 300, "R1": 3, "R2": 3, "R3": 3, "R4": 3, "R5": 3, "pillars": "prevencion",
         "environments": "nave, base_lunar", "is_ground_investigation": False, "n_publications_with_doi": 30},
        {"psi_id": "PSI-2", "acronym": "B", "title": "smoke", "tier": 1, "access_status": "available",
         "n_gold_tests": 0, "R1": 3, "R2": 3, "R3": 2, "R4": 3, "R5": 3, "pillars": "deteccion, prevencion",
         "environments": "nave", "is_ground_investigation": False, "n_publications_with_doi": 5},
        {"psi_id": "PSI-3", "acronym": None, "title": "ground lab", "tier": 3, "access_status": "experimental_table_only",
         "n_gold_tests": 0, "R1": 1, "R2": 1, "R3": 0, "R4": 0, "R5": 0, "pillars": "supresion",
         "environments": "base_lunar", "is_ground_investigation": True, "n_publications_with_doi": 0},
    ])


def test_dimensions_are_bounded_and_traceable(inv):
    d = mcda.dimension_scores(inv, "base_lunar")
    assert ((d[list(mcda.DIMENSIONS)] >= 0) & (d[list(mcda.DIMENSIONS)] <= 1)).all().all()
    row = d.set_index("psi_id")
    assert row.loc["PSI-1", "pillar_prevencion"] == pytest.approx(1.0)
    assert row.loc["PSI-2", "pillar_prevencion"] == pytest.approx(0.7)  # secondary pillar
    assert row.loc["PSI-2", "environment"] == 0 and row.loc["PSI-3", "environment"] == pytest.approx(0.6)  # ground lab
    assert row.loc["PSI-3", "maturity"] == 0 and row.loc["PSI-1", "maturity"] == pytest.approx(1.0)


def test_weights_drive_the_order(inv):
    prevention = mcda.rank(inv, weights={"pillar_prevencion": 1}, environment="nave").table
    detection = mcda.rank(inv, weights={"pillar_deteccion": 1}, environment="nave").table
    assert prevention.psi_id.iloc[0] == "PSI-1" and detection.psi_id.iloc[0] == "PSI-2"
    contrib = [c for c in prevention.columns if c.startswith("contrib_")]
    assert prevention[contrib].sum(axis=1).round(9).tolist() == prevention.score.round(9).tolist()
    assert prevention["rank"].tolist() == [1, 2, 3]


def test_invalid_inputs_fail_loudly(inv):
    with pytest.raises(ValueError):
        mcda.rank(inv, weights={"magic": 1})
    with pytest.raises(ValueError):
        mcda.rank(inv, weights={"evidence": 0})
    with pytest.raises(ValueError):
        mcda.dimension_scores(inv, "venus")
    with pytest.raises(ValueError):
        mcda.rank(inv, profile="nope")


def test_real_profiles_and_sensitivity(inv):
    for profile in ("lunar_habitat_engineer", "suppression_designer", "detection_researcher", "student"):
        r = mcda.rank(inv, profile)
        assert abs(sum(r.weights.values()) - 1) < 1e-9 and len(r.table) == 3
    s = mcda.sensitivity(inv, "student")
    assert len(s) == 2 * len(mcda.DIMENSIONS) and s.top_k_changed.between(0, 3).all()
