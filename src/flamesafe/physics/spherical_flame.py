"""Physical groups for burner-supported spherical diffusion flames (ACME CFI-G / Flame Design).

Both campaigns burn gas issuing from a porous spherical burner in microgravity. In the classical quasi-steady,
unity-Lewis-number picture the burner-stream fraction decays as xi(r) = 1 - exp(-m_tot / (4 pi rho D r)), so the flame
sheet (mixture fraction = Zst) sits at

    r_f = m_tot / (4 pi rho D * L),   L = -ln(1 - Zst)  (normal flame: fuel from the burner)
                                      L = -ln(Zst)      (inverse flame: oxidizer from the burner)

rho*D is roughly pressure-independent, so `m_tot / L` is proportional to the steady flame radius. These are scaling
groups for statistical models, not a simulation: real ISS flames are transient and lose heat by radiation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MOLAR_MASS_G_MOL = {"ethane": 30.069, "propane": 44.096, "butane": 58.122, "ethylene": 28.053}
M_N2, M_O2 = 28.013, 31.998


def mass_fraction(x: pd.Series | float, molar_mass: pd.Series | float, diluent_molar_mass: float = M_N2):
    """Mass fraction of a species at mole fraction `x` in a binary mixture with a diluent (N2 by default)."""
    return x * molar_mass / (x * molar_mass + (1 - x) * diluent_molar_mass)


def add_spherical_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Add burner-stream mass fraction `y_burner`, total burner mass flow `m_tot_mg_s`, `log_term` (L) and
    `r_ss_proxy` (= m_tot / L, proportional to the steady flame radius) for normal and inverse flames.

    Normal: the burner stream is fuel + N2 (`x_fuel`, `m_fuel_mg_s`). Inverse: O2 + N2 (`xo2`, `m_o2_mg_s`).
    Rows lacking the needed inputs get NaN, never 0.
    """
    d = df.copy()
    normal = d["flame_type"].eq("normal")
    w_fuel = d["fuel"].map(MOLAR_MASS_G_MOL)
    d["y_burner"] = np.where(normal, mass_fraction(d["x_fuel"], w_fuel), mass_fraction(d["xo2"], M_O2))
    reactant_flow = np.where(normal, d["m_fuel_mg_s"], d["m_o2_mg_s"])
    d["m_tot_mg_s"] = reactant_flow / d["y_burner"]
    zst = d["zst"].where(d["zst"].between(0, 1, inclusive="neither"))
    d["log_term"] = np.where(normal, -np.log(1 - zst), -np.log(zst))
    d["r_ss_proxy"] = d["m_tot_mg_s"] / d["log_term"]
    return d
