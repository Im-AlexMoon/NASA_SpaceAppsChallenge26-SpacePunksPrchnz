"""Stoichiometric mixture fraction and adiabatic flame temperature: textbook values and physical trends."""

from __future__ import annotations

import pytest

from flamesafe.physics import thermochem as tc


def test_zst_of_pure_fuel_in_air_matches_textbook():
    # pure propane into air: Zst ~ 0.060 ; pure ethylene into air: ~ 0.064
    assert tc.zst("propane", 1.0, 0.21) == pytest.approx(0.060, abs=0.002)
    assert tc.zst("ethylene", 1.0, 0.21) == pytest.approx(0.064, abs=0.002)


def test_zst_moves_with_dilution_and_oxygen():
    base = tc.zst("ethane", 0.3, 0.21)
    assert tc.zst("ethane", 0.3, 0.34) > base  # richer oxidizer: flame needs more fuel-stream gas
    assert tc.zst("ethane", 0.1, 0.21) > base  # more diluted fuel stream: same


def test_tad_values_and_trends():
    pytest.importorskip("cantera")
    air = tc.tad_k("propane", 1.0, 0.21)
    assert air == pytest.approx(2270, abs=40)  # stoichiometric propane-air, equilibrium with dissociation
    assert tc.tad_k("propane", 1.0, 0.34) > air + 250  # oxygen enrichment
    assert tc.tad_k("propane", 0.3, 0.21) < air  # nitrogen in the fuel stream cools the flame
    # lower pressure -> more dissociation -> slightly cooler
    assert tc.tad_k("propane", 1.0, 0.21, p_kpa=50) < tc.tad_k("propane", 1.0, 0.21, p_kpa=300)
    assert tc.tad_k("butane", 0.3, 0.30, 70.3) == pytest.approx(2470, abs=40)
