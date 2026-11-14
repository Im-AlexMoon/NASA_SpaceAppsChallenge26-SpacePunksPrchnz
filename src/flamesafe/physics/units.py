"""Explicit, reversible unit conversions. Every conversion used in silver/gold lives here + is tested."""

from __future__ import annotations

PSI_TO_KPA = 6.894757
ATM_TO_KPA = 101.325
BAR_TO_KPA = 100.0
MMHG_TO_KPA = 0.133322387415  # 101.325 / 760


def mmhg_to_kpa(x: float) -> float:
    return x * MMHG_TO_KPA


def psi_to_kpa(x: float) -> float:
    return x * PSI_TO_KPA


def atm_to_kpa(x: float) -> float:
    return x * ATM_TO_KPA


def bar_to_kpa(x: float) -> float:
    return x * BAR_TO_KPA


def pct_to_mole_fraction(pct: float) -> float:
    return pct / 100.0


def celsius_to_kelvin(c: float) -> float:
    return c + 273.15
