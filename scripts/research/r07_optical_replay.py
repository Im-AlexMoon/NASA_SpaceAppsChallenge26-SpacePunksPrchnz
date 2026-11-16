"""Replay optical contraction against supplied, independently adjudicated end labels.

The labels CSV must contain video_key, end_s and extinction_mode. The prediction
step reads only frames up to its first alert. End labels are used solely to score it.
"""

import argparse
from pathlib import Path

import pandas as pd


def first_alert(frames: pd.DataFrame) -> float | None:
    frames = frames.sort_values("t_s")
    visible = frames.loc[~frames.lights & frames.r_eq_px.notna() & frames.roundness.ge(0.55)]
    if visible.empty:
        return None
    start = float(visible.t_s.iloc[0])
    base = visible.loc[visible.t_s.lt(start + 10), "r_eq_px"]
    if len(base) < 10:
        return None
    baseline = float(base.median())
    falling_since = None
    previous = None
    for row in visible.loc[visible.t_s.ge(start + 10)].itertuples():
        if row.r_eq_px >= 0.8 * baseline:
            falling_since = None
        else:
            if falling_since is None or (previous is not None and row.t_s - previous > 1):
                falling_since = row.t_s
            if row.t_s - falling_since >= 2:
                return float(row.t_s)
        previous = row.t_s
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frames", type=Path)
    parser.add_argument("labels", type=Path)
    args = parser.parse_args()
    rows = []
    for label in pd.read_csv(args.labels).itertuples():
        path = args.frames / f"{label.video_key}.parquet"
        if not path.is_file():
            continue
        frames = pd.read_parquet(path)
        alert = first_alert(frames)
        rows.append({
            "video_key": label.video_key,
            "termination": label.extinction_mode,
            "end_s": label.end_s,
            "lead_s": label.end_s - alert if alert is not None and alert < label.end_s else None,
        })
    if not rows:
        raise SystemExit("No labeled frame files were found. Provide the adjudicated labels and per-frame Parquet.")
    results = pd.DataFrame(rows)
    print(results.groupby("termination").lead_s.agg(["size", "count", "median"]).to_string())
    cuts = results[results.termination.eq("flow_terminated")]
    if cuts.end_s.sum() > 0:
        print(f"Alerts per video hour before flow cutoff: {cuts.lead_s.notna().sum() * 3600 / cuts.end_s.sum():.2f}")
    print("Exploratory replay. Use separate days for threshold tuning and validation.")


if __name__ == "__main__":
    main()
