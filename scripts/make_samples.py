"""Regenerate the tiny committed gold fixtures in data/sample/ (used by offline tests / CI).

Deterministic, stratified slices of the real gold tables (NASA PSI data, CC0). Keeps every edge case the contracts
care about: flash outcomes, EventData-sourced outcomes, missing outcomes, RAMP qualifiers, inverse flames, the FLEX
p=0 row, CFI rows with and without inferred x_co2. Run after `flamesafe gold`:  python scripts/make_samples.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from flamesafe import config

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample"


def pick(df: pd.DataFrame, masks: list[pd.Series], per: int = 3) -> pd.DataFrame:
    idx: list[int] = []
    for m in masks:
        idx += [i for i in df.index[m.fillna(False)].tolist() if i not in idx][:per]
    return df.loc[sorted(idx)].reset_index(drop=True)


def main() -> None:
    gold = config.data_dir() / "gold"
    g = pd.read_parquet(gold / "gas_flame_tests.parquet")
    gs = pick(g, [g.ignition_outcome == "flash", g.outcome_source == "eventdata", g.outcome_source == "none",
                  g.qualifier.notna(), (g.campaign == "CFI-G") & (g.flame_type == "inverse") & (g.xo2 >= 0.5),
                  (g.campaign == "CFI-G") & (g.flame_type == "normal") & g.cool_flame.fillna(False),
                  g.ignited == False, g.tad_k.isna()])  # noqa: E712
    d = pd.read_parquet(gold / "droplet_tests.parquet")
    ds = pick(d, [d.quality_flags.notna() & (d.campaign == "FLEX"), (d.campaign == "FLEX") & (d.x_co2 > 0),
                  (d.campaign == "FLEX") & (d.x_he > 0), d.test_end == "completion",
                  (d.campaign == "CFI") & d.k_hot_mm2_s.notna(), (d.campaign == "CFI") & ~d.x_co2_inferred,
                  (d.campaign == "CFI") & d.fuel_blend.notna()])
    r = pd.read_parquet(gold / "droplet_reference_points.parquet")
    rs = pick(r, [r.role == k for k in ("experiment", "model", "error_bar", "unknown")], per=4)
    inv = pd.read_parquet(gold / "investigations.parquet")
    pubs = pd.read_parquet(gold / "publications.parquet")
    ps = pick(pubs, [pubs.n_records > 1, pubs.doi.isna(), pubs.n_records == 1], per=3)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, df in {"gas_flame_tests": gs, "droplet_tests": ds, "droplet_reference_points": rs,
                     "investigations": inv, "publications": ps}.items():
        df.to_parquet(OUT / f"gold_{name}.parquet", index=False)
        print(f"{name}: {len(df)} rows")


if __name__ == "__main__":
    main()
