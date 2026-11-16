"""Describe RQ2 coverage without pooling campaigns or assuming missing measurements are zero."""

import pandas as pd

from flamesafe import config


def main() -> None:
    gold = config.data_dir() / "gold"
    trials = pd.read_parquet(gold / "droplet_tests.parquet")
    points = pd.read_parquet(gold / "droplet_reference_points.parquet")
    trials = trials.assign(co2_origin="reported or missing")
    trials.loc[trials.x_co2_inferred.fillna(False), "co2_origin"] = "inferred"
    measurements = ["d0_mm", "d_ext_hot_mm", "d_ext_cool_mm", "k_hot_mm2_s", "k_cool_mm2_s"]
    groups = trials.groupby(["campaign", "fuel"], dropna=False)
    coverage = groups[measurements].count().join(groups.size().rename("trials"))
    print(coverage.to_string())
    print("\nCO2 origin by campaign")
    print(trials.groupby(["campaign", "co2_origin"], dropna=False).size().to_string())
    print("\nDigitized references by role. These counts are not trials.")
    print(points["role"].value_counts(dropna=False).to_string())
    print("\nPressure, diluent and initial-diameter overlap require review before pooling campaigns.")


if __name__ == "__main__":
    main()
