import math

from flamesafe import config
from flamesafe.physics import units
from flamesafe.physics.atmospheres import REFERENCE_ATMOSPHERES


def test_configs_load():
    for name in ("sources", "pipeline", "models", "rag"):
        assert isinstance(config.load(name), dict)


def test_unit_roundtrip():
    assert math.isclose(units.psi_to_kpa(14.7), 101.35, rel_tol=1e-3)
    assert math.isclose(units.atm_to_kpa(1.0), 101.325)


def test_lunar_atmosphere_has_higher_o2_fraction_but_lower_partial_pressure_than_suit():
    lunar = REFERENCE_ATMOSPHERES["lunar_base_upper"]
    suit = REFERENCE_ATMOSPHERES["spacesuit"]
    earth = REFERENCE_ATMOSPHERES["earth_sea_level"]
    assert lunar.o2_mole_fraction > earth.o2_mole_fraction
    assert lunar.o2_partial_pressure_kpa < suit.o2_partial_pressure_kpa
