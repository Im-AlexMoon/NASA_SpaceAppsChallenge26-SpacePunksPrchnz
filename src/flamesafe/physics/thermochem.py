"""Stoichiometric mixture fraction (Zst) and adiabatic flame temperature (Tad) of a diffusion flame.

A diffusion flame burns where the fuel stream (fuel + N2) and the oxidizer stream (O2 + N2) meet in stoichiometric
proportion. `zst` is the mass fraction of fuel-stream gas in that mixture; `tad_k` is the constant-pressure,
constant-enthalpy chemical-equilibrium temperature of that mixture (dissociation included).

Both are **calculated** quantities, exactly like the `zst` / `tad_k` columns published by the investigators, and must
never be mixed with measured temperatures. Tad needs Cantera (thermodynamic data only: NASA polynomials shipped with
it); Zst is pure stoichiometry. Used to place a cabin atmosphere on the same physical axes as the experiments.
"""

from __future__ import annotations

from functools import lru_cache

from flamesafe.physics.spherical_flame import M_N2, M_O2, MOLAR_MASS_G_MOL, mass_fraction

# name in Cantera's nasa_gas.yaml, and moles of O2 per mole of fuel for complete combustion (CxHy: x + y/4)
FUELS = {
    "ethane": ("C2H6", 3.5),
    "propane": ("C3H8", 5.0),
    "butane": ("C4H10,n-butane", 6.5),
    "ethylene": ("C2H4", 3.0),
}
PRODUCTS = ["O2", "N2", "CO2", "H2O", "CO", "H2", "OH", "O", "H", "NO"]
T_REACTANTS_K = 298.15


def zst(fuel: str, x_fuel: float, xo2: float) -> float:
    """Stoichiometric mixture fraction for a fuel/N2 stream (mole fraction `x_fuel`) and an O2/N2 stream (`xo2`)."""
    _, nu = FUELS[fuel]
    y_f = mass_fraction(x_fuel, MOLAR_MASS_G_MOL[fuel])
    y_o = mass_fraction(xo2, M_O2)
    s = nu * M_O2 / MOLAR_MASS_G_MOL[fuel]  # kg of O2 per kg of fuel
    return y_o / (s * y_f + y_o)


@lru_cache(maxsize=8)
def _gas(fuel: str):
    import cantera as ct

    species = ct.Species.list_from_file("nasa_gas.yaml")
    wanted = {FUELS[fuel][0], *PRODUCTS}
    return ct.Solution(thermo="ideal-gas", species=[s for s in species if s.name in wanted])


def tad_k(fuel: str, x_fuel: float, xo2: float, p_kpa: float = 101.325, t0_k: float = T_REACTANTS_K) -> float:
    """Equilibrium adiabatic temperature (K) of the stoichiometric mixture of the two streams at pressure `p_kpa`."""
    name, nu = FUELS[fuel]
    gas = _gas(fuel)
    # per mole of fuel: N2 carried by the fuel stream, O2 needed, N2 carried by the oxidizer stream
    n2_fuel = (1 - x_fuel) / x_fuel
    n2_ox = nu * (1 - xo2) / xo2
    gas.TPX = t0_k, p_kpa * 1000.0, {name: 1.0, "O2": nu, "N2": n2_fuel + n2_ox}
    gas.equilibrate("HP")
    return float(gas.T)


__all__ = ["FUELS", "M_N2", "tad_k", "zst"]
