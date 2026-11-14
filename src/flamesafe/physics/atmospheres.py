"""Reference cabin atmospheres used across analysis, models and dashboard.

Values must match docs/04_physics/HABITAT_ATMOSPHERES.md (single source of truth for citations).
"""

from __future__ import annotations

from dataclasses import dataclass

PSI_TO_KPA = 6.894757


@dataclass(frozen=True)
class Atmosphere:
    name: str
    total_pressure_psi: float
    o2_mole_fraction: float
    gravity_g: float  # in units of Earth g

    @property
    def total_pressure_kpa(self) -> float:
        return self.total_pressure_psi * PSI_TO_KPA

    @property
    def o2_partial_pressure_kpa(self) -> float:
        return self.total_pressure_kpa * self.o2_mole_fraction


REFERENCE_ATMOSPHERES: dict[str, Atmosphere] = {
    "earth_sea_level": Atmosphere("Earth sea level", 14.7, 0.209, 1.0),
    "iss_cabin": Atmosphere("ISS cabin", 14.7, 0.21, 0.0),
    "spacesuit": Atmosphere("Spacesuit (EMU-class)", 4.3, 1.00, 0.0),
    # Challenge statement: lunar base / rover likely >=30% O2 at <=10.2 psi
    "lunar_base_upper": Atmosphere("Lunar base (challenge bound)", 10.2, 0.30, 0.165),
    # NASA exploration atmosphere studies (verify citation in HABITAT_ATMOSPHERES.md)
    "exploration_8p2_34": Atmosphere("Exploration atm 8.2 psi / 34% O2", 8.2, 0.34, 0.165),
    "mars_surface_habitat": Atmosphere("Mars habitat (assumed = exploration atm)", 8.2, 0.34, 0.38),
}
