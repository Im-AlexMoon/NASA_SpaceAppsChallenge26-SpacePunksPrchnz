"""ADR-0005 · Per-test features from the raw ACME time series (CFI-G / Flame Design `*_data.csv`).

One raw file = one test: a metadata preamble line, a header line and ~125 Hz samples of mass-flow controllers (MFC),
photomultipliers (PMT), radiometers, thermocouples and pressure transducers. This module reduces each file to one row:

* when the burner flow started and stopped;
* when a flame was seen by the PMTs (visible emission) and when it disappeared;
* whether the flame died on its own (well before the flow stopped) or was still alive at the flow cut;
* radiometer, burner-thermocouple and pressure summaries, and an oscillation index before the flame ended.

Signals stay in **raw volts** (no calibration is published in the files): features are durations, ratios and relative
changes, never absolute temperatures or heat fluxes. Missing signals give NaN, never 0.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from flamesafe import config

DATA_FILE = re.compile(r"^(PSI-\d+)_Raw Data_(\d{5}[A-Z]\d+)(?:_(\d+))?_data\.csv$")  # optional re-run suffix
PMT_ON_V = 0.10          # PMTs read ~0.00 V in the dark and 0.5-4.5 V with a flame
FLOW_ON_FRACTION = 0.5   # of each controller's own robust maximum
MIN_FLOW_V = 0.02        # a controller whose maximum stays below this never flowed
SELF_EXT_MARGIN_S = 1.0  # flame gone more than this before the flow stops -> self-extinguished
MIN_SEGMENT_S = 0.10
FLOW_GAP_S = 2.0         # flow interruptions shorter than this belong to the same flow period
IGNITER_MARGIN_S = 1.5   # emission must outlast the igniter by this much to count as a sustained flame
DEFAULT_IGNITER_S = 3.0
OSC_REL_RMS = 0.05       # fast fluctuation above 5 % of the signal level counts as oscillation


def parse_stream(path: Path) -> tuple[dict[str, str], pd.DataFrame]:
    """Read one `*_data.csv`: preamble as a dict and samples with `t` in seconds from the first sample."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        first = fh.readline().strip()
    parts = [p.strip() for p in first.split(",")]
    meta = {"start_stamp": parts[0]}
    meta.update(dict(p.split(": ", 1) for p in parts[1:] if ": " in p))
    df = pd.read_csv(path, skiprows=1, low_memory=False, on_bad_lines="skip")  # a few files have ragged lines
    df = df[pd.to_datetime(df["Time"], format="%H:%M:%S:%f", errors="coerce").notna()].reset_index(drop=True)
    clock = pd.to_datetime(df["Time"], format="%H:%M:%S:%f", errors="coerce")
    t = (clock - clock.iloc[0]).dt.total_seconds().to_numpy()
    t = np.where(t < -43200, t + 86400, t)  # a test that crosses midnight
    return meta, df.assign(t=t).drop(columns="Time").apply(pd.to_numeric, errors="coerce")


def _segments(mask: np.ndarray, t: np.ndarray, min_len: float = MIN_SEGMENT_S) -> list[tuple[float, float]]:
    """(start, end) times of the runs where `mask` is True and lasts at least `min_len` seconds."""
    if not mask.any():
        return []
    edges = np.diff(np.r_[0, mask.astype(int), 0])
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1) - 1
    return [(float(t[a]), float(t[b])) for a, b in zip(starts, ends, strict=True) if t[b] - t[a] >= min_len]


def _smooth(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, center=True, min_periods=1).median().to_numpy()


def flow_window(df: pd.DataFrame) -> tuple[float, float]:
    """Start and stop of the main gas flow: the longest period with any MFC above half of its own maximum.

    Short priming pulses fired earlier in the script (while the chamber lights are still on) are not the test flow.
    """
    t = df["t"].to_numpy()
    on = np.zeros(len(df), bool)
    for col in [c for c in df.columns if c.startswith("MFCA")]:
        x = _smooth(df[col].to_numpy(float), 9)
        flowing = x[x > MIN_FLOW_V]
        if len(flowing) > 50:  # the typical flowing level, so a tall priming spike does not hide a low test flow
            on |= x > max(MIN_FLOW_V, FLOW_ON_FRACTION * np.median(flowing))
    merged: list[list[float]] = []
    for a, b in _segments(on, t, 0.5):
        if merged and a - merged[-1][1] < FLOW_GAP_S:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    if not merged:
        return np.nan, np.nan
    a, b = max(merged, key=lambda seg: seg[1] - seg[0])
    return a, b


def flame_segments(df: pd.DataFrame, t_flow_on: float) -> list[tuple[float, float]]:
    """Intervals with visible emission on any PMT, counted from shortly before the flow starts.

    Before a test the chamber lights keep the PMTs high; they go dark just before the flow opens, so anything earlier
    than `t_flow_on - 1 s` is ignored.
    """
    pmt = [c for c in df.columns if re.fullmatch(r"PMT\d", c)]
    if not pmt or np.isnan(t_flow_on):
        return []
    t = df["t"].to_numpy()
    signal = _smooth(df[pmt].max(axis=1).to_numpy(float), 5)
    return _segments((signal > PMT_ON_V) & (t >= t_flow_on - 1.0), t)


def _radiometers(df: pd.DataFrame) -> list[str]:
    cols = [c for c in df.columns if c.startswith("Radiometer") and "Offset" not in c and not c.endswith("CJ")]
    lo = [c for c in cols if c.endswith("LoGain")]
    return lo or [c for c in cols if not c.endswith("HiGain")]


def classify_flame(flame_on_s: float, igniter_s: float | None) -> str | None:
    """`none` (no emission), `transient` (no longer than the igniter glow plus a margin) or `sustained`."""
    if flame_on_s is None or np.isnan(flame_on_s):
        return "none"
    igniter = DEFAULT_IGNITER_S if igniter_s is None or np.isnan(igniter_s) else igniter_s
    return "sustained" if flame_on_s > igniter + IGNITER_MARGIN_S else "transient"


def oscillation_lead(t: np.ndarray, x: np.ndarray, t_start: float, t_end: float) -> float:
    """Seconds before `t_end` during which the signal oscillated without interruption (0 if it ended calmly).

    Oscillation = 1-s rolling RMS of the detrended signal above OSC_REL_RMS of its local level.
    """
    m = (t >= t_start + 1.0) & (t <= t_end - 0.1)
    if m.sum() < 250:
        return np.nan
    seg, ts_ = pd.Series(x[m]), t[m]
    n = max(int(1.0 / np.median(np.diff(ts_))), 5)
    trend = seg.rolling(n, center=True, min_periods=1).mean()
    rel = ((seg - trend) ** 2).rolling(n, center=True, min_periods=1).mean() ** 0.5 / trend.abs().clip(lower=1e-6)
    calm = np.flatnonzero((rel < OSC_REL_RMS).to_numpy())
    if len(calm) == 0:
        return float(ts_[-1] - ts_[0])
    return float(ts_[-1] - ts_[calm[-1]])


def _oscillation(t: np.ndarray, x: np.ndarray, t_end: float, window: float = 4.0) -> tuple[float, float]:
    """Relative RMS of the fast fluctuation in the last `window` seconds before `t_end`, and its dominant frequency."""
    m = (t >= t_end - window) & (t <= t_end - 0.2)
    if m.sum() < 100:
        return np.nan, np.nan
    seg, ts = x[m], t[m]
    dt = np.median(np.diff(ts))
    trend = pd.Series(seg).rolling(max(int(1.0 / dt), 3), center=True, min_periods=1).mean().to_numpy()
    resid = seg - trend
    level = np.abs(trend).mean()
    spec = np.abs(np.fft.rfft(resid * np.hanning(len(resid))))
    freq = np.fft.rfftfreq(len(resid), dt)
    band = (freq >= 0.5) & (freq <= 25)
    f_dom = float(freq[band][spec[band].argmax()]) if band.any() else np.nan
    return (float(resid.std() / level) if level > 0 else np.nan), f_dom


def extract_features(meta: dict[str, str], df: pd.DataFrame) -> dict[str, object]:
    """One row of features for a test. See the module docstring for definitions."""
    t = df["t"].to_numpy()
    out: dict[str, object] = {"n_samples": len(df), "record_s": float(t[-1] - t[0]),
                              "sample_hz": float(1 / np.median(np.diff(t)))}
    t_on, t_off = flow_window(df)
    out |= {"t_flow_on_s": t_on, "t_flow_off_s": t_off, "flow_duration_s": t_off - t_on}

    segs = flame_segments(df, t_on)
    out["flame_seen"] = bool(segs)
    out["n_flame_segments"] = len(segs)
    if segs:
        t_ign, t_end = segs[0][0], segs[-1][1]
        truncated = t_end >= t[-1] - 0.2  # record stops with the flame still on
        out |= {"t_ignition_s": t_ign, "t_flame_end_s": t_end, "ignition_delay_s": t_ign - t_on,
                "flame_duration_s": t_end - t_ign, "flame_on_s": float(sum(b - a for a, b in segs)),
                "lead_before_flow_off_s": t_off - t_end, "record_truncated": bool(truncated),
                "ts_extinction_mode": ("unknown" if truncated or np.isnan(t_off) else
                                       "self_extinguished" if t_off - t_end > SELF_EXT_MARGIN_S else "flow_terminated")}
    else:
        out |= {"t_ignition_s": np.nan, "t_flame_end_s": np.nan, "ignition_delay_s": np.nan,
                "flame_duration_s": np.nan, "flame_on_s": np.nan, "lead_before_flow_off_s": np.nan,
                "record_truncated": False, "ts_extinction_mode": None}

    rad = _radiometers(df)
    out["n_radiometers"] = len(rad)
    if rad and segs:
        base = df.loc[df["t"] < max(t_on - 1.0, 1.0), rad].median()
        r = (df[rad] - base).mean(axis=1).to_numpy(float)  # mean of baseline-corrected channels, volts
        on = (t >= t_ign) & (t <= t_end)
        peak = float(np.nanmax(r[on])) if on.any() else np.nan
        i_peak = int(np.nanargmax(np.where(on, r, -np.inf)))
        last = (t >= t_end - 1.0) & (t <= t_end)
        rms, f_dom = _oscillation(t, r, t_end)
        out |= {"rad_peak_v": peak, "rad_t_peak_frac": float((t[i_peak] - t_ign) / max(t_end - t_ign, 1e-9)),
                "rad_integral_v_s": float(np.trapezoid(np.clip(r[on], 0, None), t[on])),
                "rad_end_over_peak": float(np.nanmean(r[last]) / peak) if peak > 0 else np.nan,
                "rad_osc_rms_rel": rms, "rad_osc_freq_hz": f_dom,
                "rad_osc_lead_s": oscillation_lead(t, r, t_ign, t_end)}
    else:
        out |= dict.fromkeys(["rad_peak_v", "rad_t_peak_frac", "rad_integral_v_s", "rad_end_over_peak",
                              "rad_osc_rms_rel", "rad_osc_freq_hz", "rad_osc_lead_s"], np.nan)

    pmt = [c for c in df.columns if re.fullmatch(r"PMT\d", c)]
    out["pmt_osc_lead_s"] = np.nan
    if pmt and segs:
        on = (t >= t_ign) & (t <= t_end)
        # the least saturated PMT that still sees the flame: saturation (~4.5 V) hides oscillations
        usable = [c for c in pmt if 0.2 < np.nanmedian(df.loc[on, c]) < 4.0]
        if usable:
            best = min(usable, key=lambda c: np.nanmedian(df.loc[on, c]))
            out["pmt_osc_lead_s"] = oscillation_lead(t, df[best].to_numpy(float), t_ign, t_end)

    if "TCBurner" in df:
        tc = _smooth(df["TCBurner"].to_numpy(float), 25)
        base = float(np.nanmedian(tc[t < max(t_on - 1.0, 1.0)])) if np.isfinite(t_on) else np.nan
        out |= {"tc_burner_rise_v": float(np.nanmax(tc) - base),
                "tc_burner_t_peak_s": float(t[int(np.nanargmax(tc))]),
                "tc_burner_peak_at_flow_off": bool(abs(t[int(np.nanargmax(tc))] - t_off) < 1.5) if np.isfinite(t_off) else False}
    for col in ("PTA2", "PTA3"):
        if col in df:
            p = _smooth(df[col].to_numpy(float), 25)
            p0 = float(np.nanmedian(p[: max(int(len(p) * 0.05), 10)]))
            out[f"{col.lower()}_rel_rise"] = float((np.nanmax(p) - p0) / p0) if p0 > 0 else np.nan
    out["preamble_test_point"] = meta.get("Test Point")
    return out


# ------------------------------------------------------------------------------------------- operator / script logs

TP_EVENTS = {  # label in `<test>_TP.txt` -> output column (script's own event clock, GMT)
    "Script start": "tp_script_start", "MFCs on for priming": "tp_mfcs_on", "Ignition and retraction": "tp_ignition",
    "Constant flow": "tp_constant_flow", "MFCs off": "tp_mfcs_off", "Extinction detected": "tp_extinction_detected",
}
CONFIG_KEYS = {  # key in the as-run test configuration -> output column
    "flowTimeoutSec": "cfg_flow_timeout_s", "igniterIgnitionPowerV": "cfg_igniter_power_v",
    "igniterIgnitionDurationMs": "cfg_igniter_duration_ms", "igniterPreheatPowerV": "cfg_igniter_preheat_v",
    "igniterPreheatTimeMs": "cfg_igniter_preheat_ms", "extinctionDetectionStopsTest": "cfg_extinction_stops_test",
    "useIgnitionDetection": "cfg_use_ignition_detection",
}


def parse_tp_log(path: Path) -> dict[str, object]:
    """Event timestamps written by the test script (`*_TP.txt`). `***` (event did not happen) becomes NaT."""
    out: dict[str, object] = dict.fromkeys(TP_EVENTS.values(), pd.NaT)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        label, sep, value = line.partition(":")
        col = TP_EVENTS.get(label.strip())
        if sep and col:
            out[col] = pd.to_datetime(value.strip(), errors="coerce")
    return out


def parse_test_config(path: Path) -> dict[str, object]:
    """Selected `key:value,` settings of the as-run test configuration (igniter, flow timeout, extinction detection)."""
    out: dict[str, object] = dict.fromkeys(CONFIG_KEYS.values(), np.nan)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        key, sep, value = line.strip().rstrip(",").partition(":")
        col = CONFIG_KEYS.get(key.strip())
        if sep and col:
            v = value.strip()
            out[col] = {"true": True, "false": False}.get(v.lower(), pd.to_numeric(v, errors="coerce"))
    return out


def _notes(folder: Path, psi_id: str, test_id: str) -> dict[str, object]:
    row: dict[str, object] = {}
    tp = folder / f"{psi_id}_Raw Data_{test_id}_TP.txt"
    row |= parse_tp_log(tp) if tp.exists() else dict.fromkeys(TP_EVENTS.values(), pd.NaT)
    cfg = next((p for p in (folder / f"{psi_id}_Raw Data_as run{test_id}.txt", folder / f"{psi_id}_Raw Data_{test_id}.txt")
                if p.exists()), None)
    row |= parse_test_config(cfg) if cfg else dict.fromkeys(CONFIG_KEYS.values(), np.nan)
    row["config_file"] = cfg.name if cfg else None
    comments = folder / f"{psi_id}_Raw Data_{test_id}_Comments.txt"
    row["operator_comments"] = (comments.read_text(encoding="utf-8", errors="replace").strip() or None
                                if comments.exists() else None)
    for a, b, name in [("tp_ignition", "tp_extinction_detected", "tp_ignition_to_extinction_s"),
                       ("tp_ignition", "tp_mfcs_off", "tp_ignition_to_mfcs_off_s"),
                       ("tp_extinction_detected", "tp_mfcs_off", "tp_extinction_to_mfcs_off_s")]:
        delta = row[b] - row[a] if pd.notna(row[a]) and pd.notna(row[b]) else pd.NaT
        row[name] = delta.total_seconds() if pd.notna(delta) else np.nan
    row["tp_extinction_logged"] = bool(pd.notna(row["tp_extinction_detected"])) if tp.exists() else None
    return row


def build_features(files_root: Path | None = None, out_path: Path | None = None) -> pd.DataFrame:
    """Reduce every downloaded `*_data.csv` of PSI-159 / PSI-10 to one row and write the silver table."""
    root = files_root or config.data_dir() / "bronze" / "files"
    rows = []
    for psi in ("PSI-159", "PSI-10"):
        for path in sorted((root / psi).glob("*_data.csv")):
            m = DATA_FILE.match(path.name)
            if not m:
                continue
            row: dict[str, object] = {"psi_id": m.group(1), "test_id": m.group(2), "file_variant": m.group(3),
                                      "source_file": path.name}
            try:
                meta, df = parse_stream(path)
                row |= extract_features(meta, df)
                row["parse_error"] = None
            except Exception as exc:  # noqa: BLE001 - recorded per file, never hidden
                row["parse_error"] = f"{type(exc).__name__}: {exc}"[:200]
            row |= _notes(path.parent, m.group(1), m.group(2))
            igniter_ms = row.get("cfg_igniter_duration_ms")
            row["ts_flame_class"] = (None if row["parse_error"] else classify_flame(
                row.get("flame_on_s", np.nan), igniter_ms / 1000 if pd.notna(igniter_ms) else None))
            rows.append(row)
    table = pd.DataFrame(rows)
    for col in TP_EVENTS.values():
        table[col] = pd.to_datetime(table[col], errors="coerce")
    out_path = out_path or config.data_dir() / "silver" / "tables" / "acme__timeseries_features.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(out_path, index=False)
    return table
