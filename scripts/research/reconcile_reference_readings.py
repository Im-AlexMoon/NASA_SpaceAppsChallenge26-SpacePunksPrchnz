"""Reconcile the published F-03/F-04 quantities with local Gold and the M1 notebook."""

from pathlib import Path

import pandas as pd
import yaml
from lifelines import KaplanMeierFitter

from flamesafe import config
from flamesafe.models import readings


def main() -> None:
    gas = pd.read_parquet(config.data_dir() / "gold" / "gas_flame_tests.parquet")
    estimates = {r["key"]: r for r in readings.reference_readings(readings.load(), gas)}
    expected = {
        "iss_cabin": (35, 23, 23, 0, 9.0, 9.0),
        "exploration_8p2_34": (19, 16, 12, 4, 62.5, 88.0),
    }
    for scenario, values in expected.items():
        near = estimates[scenario]["nearby"]
        cohort = pd.DataFrame(near["tests"])
        cohort = cohort.loc[
            cohort.ignition_outcome.eq("yes") & cohort.burn_time_s.gt(0)
            & cohort.extinction_mode.isin(["self_extinguished", "flow_terminated"])
        ]
        km = KaplanMeierFitter().fit(cohort.burn_time_s, cohort.extinction_mode.eq("self_extinguished"))
        actual = (
            near["n_tests"], near["n_ignited"], near["n_self_extinguished"], near["n_flow_cut"],
            near["median_burn_s_self_extinguished"], km.median_survival_time_,
        )
        if actual != values:
            raise ValueError(f"{scenario} changed from the notebook baseline: {actual!r}. Review F-03.")
        print(f"{scenario}: {actual}, fuels={near['fuel_counts']}")
    if estimates["exploration_8p2_34"]["nearby"]["same_fuel_tests"]:
        raise ValueError("The exploration fuel coverage changed; review F-03.")
    lunar = estimates["lunar_base_upper"]
    if lunar["nearby"]["n_tests"] or lunar["gravity_effect"]["tier"] != "C":
        raise ValueError("Lunar scope changed; review F-04.")
    if lunar["prediction"]["median_burn_s_90ci"] != [48.2, 72.3]:
        raise ValueError("The lunar model interval changed; review F-04.")
    findings = config.ROOT / "docs" / "03_data_science" / "findings"
    registry = {item["id"]: item["key_numbers"] for item in yaml.safe_load(
        (findings / "index.yaml").read_text(encoding="utf-8")
    )["findings"]}
    observed = registry["F-03"][:2]
    for item, key in zip(observed, expected, strict=True):
        near = estimates[key]["nearby"]
        if (item["value"], item["n"]) != (near["median_burn_s_self_extinguished"], near["n_self_extinguished"]):
            raise ValueError(f"F-03 and the observation for {key} disagree.")
    if registry["F-04"][1]["value"] != lunar["prediction"]["median_burn_s"]:
        raise ValueError("F-04 disagrees with the lunar prediction.")
    for name in ("F-01.md", "F-02.md", "F-03.md", "F-04.md", "F-05.md"):
        if not (findings / name).is_file():
            raise FileNotFoundError(Path(findings, name))
    print(f"Lunar reference: {lunar['prediction']['median_burn_s']} s in microgravity, no nearby tests.")


if __name__ == "__main__":
    main()
