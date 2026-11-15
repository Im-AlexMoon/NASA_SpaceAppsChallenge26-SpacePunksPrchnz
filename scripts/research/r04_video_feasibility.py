"""Research iteration 4 (2026-11-15): can the ISS ops-camera video measure the spherical flame? (ADR-0009, phase 1)

For each sample video: frame size and rate, when the chamber lights go off, the flame's equivalent radius per frame
(largest bright region on the dark background), the mean brightness of the flame pixels (soot glow) and how long the
flame is visible after the igniter glare. Compared with the investigator's burn time and the time-series detector.

Scale: the porous spherical burner is 6.35 mm in diameter (CFI-G final report, PSI-159); `--burner-px` converts pixels to
mm once the burner has been measured on a lit frame. Brightness is NOT comparable between tests: the ops-camera gain was
sometimes adjusted for dim flames (same report).

Needs `flamesafe video-samples` and opencv-python-headless. Run: python scripts/research/r04_video_feasibility.py
"""

from __future__ import annotations

import argparse
import os
import re

import duckdb
import numpy as np
import pandas as pd

from flamesafe import config

os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "-8")  # the downlink stream has benign decode warnings
import cv2  # noqa: E402

BURNER_DIAMETER_MM = 6.35
LIGHTS_ON_MEAN = 60      # mean gray level with the chamber lights on (~104) vs dark (~4)
FLAME_LEVEL = 28         # 8-bit level separating flame from the dark background after a 5x5 blur
MIN_RADIUS_PX = 10       # below this it is sensor noise / hot pixels (~3.5 px)
GLARE_SAT_FRAC = 0.01    # frames with >1 % saturated pixels are igniter glare


def measure(path: str, step: int = 3) -> pd.DataFrame:
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    rows, i = [], 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        i += 1
        if i % step:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        row = {"t": i / fps, "lights": bool(gray.mean() > LIGHTS_ON_MEAN), "sat_frac": float((gray >= 250).mean()),
               "r_eq_px": np.nan, "roundness": np.nan, "brightness": np.nan}
        if not row["lights"]:
            level = cv2.GaussianBlur(frame.max(axis=2), (5, 5), 0)
            mask = cv2.morphologyEx((level > FLAME_LEVEL).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                r_eq = np.sqrt(cv2.contourArea(c) / np.pi)
                if r_eq >= MIN_RADIUS_PX:
                    (_, _), r_enc = cv2.minEnclosingCircle(c)
                    inside = np.zeros_like(mask)
                    cv2.drawContours(inside, [c], -1, 1, -1)
                    row |= {"r_eq_px": r_eq, "roundness": r_eq / r_enc, "brightness": float(level[inside > 0].mean())}
        rows.append(row)
    return pd.DataFrame(rows).assign(fps=fps, width=int(cap.get(3)), height=int(cap.get(4)))


def summarize(d: pd.DataFrame, px_per_mm: float | None) -> dict[str, object]:
    flame = d[d.r_eq_px.notna()]
    steady = flame[flame.sat_frac < GLARE_SAT_FRAC]
    out = {"frame": f"{d.width.iloc[0]}x{d.height.iloc[0]} @ {d.fps.iloc[0]:.2f} fps",
           "lights_off_s": d.loc[~d.lights, "t"].min(),
           "flame_visible_s": flame.t.max() - flame.t.min() if len(flame) else np.nan,
           "after_glare_s": steady.t.max() - steady.t.min() if len(steady) else np.nan,
           "r_steady_px": steady.r_eq_px.median(), "roundness": steady.roundness.median()}
    if len(steady):
        b = steady.set_index("t").brightness.rolling(9, center=True, min_periods=1).median()
        t_peak = b.idxmax()
        dim = b[b.index > t_peak]
        t_dim = dim[dim < b.max() * 0.5].index.min() if (dim < b.max() * 0.5).any() else np.nan
        out |= {"glow_peak_after_ignition_s": t_peak - flame.t.min(),
                "glow_halved_before_end_s": flame.t.max() - t_dim if np.isfinite(t_dim) else np.nan}
    if px_per_mm:
        out["r_steady_mm"] = out["r_steady_px"] / px_per_mm
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--burner-px", type=float, default=None, help="burner diameter measured on a lit frame, in pixels")
    args = ap.parse_args()
    px_per_mm = args.burner_px / BURNER_DIAMETER_MM if args.burner_px else None
    con = duckdb.connect(str(config.data_dir() / "gold" / "flamesafe.duckdb"), read_only=True)
    gold = con.sql("SELECT test_id, flame_type, fuel, xo2, p_kpa, burn_time_s, extinction_mode FROM gas_flame_tests").df()
    con.close()
    feats = pd.read_parquet(config.data_dir() / "silver" / "tables" / "acme__timeseries_features.parquet")
    rows = []
    for path in sorted((config.data_dir() / "bronze" / "files" / "PSI-159").glob("*vlc-record*.ts")):
        test_id = re.search(r"(\d{5}[A-Z]\d+)", path.name).group(1)
        s = summarize(measure(str(path)), px_per_mm)
        ref = gold.set_index("test_id").loc[test_id]
        ts = feats.set_index("test_id").flame_duration_s.get(test_id, np.nan)
        rows.append({"test_id": test_id, "flame": ref.flame_type, "fuel": ref.fuel, "xo2": ref.xo2, "p_kpa": ref.p_kpa,
                     "pi_burn_s": ref.burn_time_s, "pi_mode": ref.extinction_mode, "ts_duration_s": ts, **s})
    pd.set_option("display.width", 240)
    print(pd.DataFrame(rows).round(2).T.to_string())


if __name__ == "__main__":
    main()
