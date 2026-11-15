"""ADR-0005: per-test feature extraction from synthetic ACME streams with a known timeline."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from flamesafe.pipeline import timeseries as ts

HZ = 125


def _write_stream(path, flame_end: float, flow_off: float = 60.0, oscillate: bool = False, lights: bool = True):
    """Lights on until 19 s, flow from 20 s, flame from 21 s to `flame_end`, flow stops at `flow_off`, 80 s record."""
    t = np.arange(0, 80, 1 / HZ)
    rng = np.random.default_rng(0)
    flow = np.where((t >= 20) & (t <= flow_off), 2.0, 0.0) + rng.normal(0, 0.002, len(t))
    flame = (t >= 21) & (t <= flame_end)
    pmt = np.where(flame, 3.0, 0.0) + (np.where(t < 19, 4.4, 0.0) if lights else 0.0) + rng.normal(0, 0.003, len(t))
    rad = -0.02 + np.where(flame, 0.2 + 0.02 * (t - 21), 0.0)
    if oscillate:
        rad = rad + np.where(flame & (t > flame_end - 4), 0.15 * np.sin(2 * np.pi * 2.0 * t), 0.0)
    rad = rad + np.where(t > flame_end, 0.3 * np.exp(-(t - flame_end) / 8), 0.0)  # slow thermal tail, no flame
    clock = (pd.Timestamp("2021-01-01 23:59:30") + pd.to_timedelta(t, unit="s")).strftime("%H:%M:%S:%f").str[:-3]
    df = pd.DataFrame({"Time": clock, "MFCA1StaticMixerFlow": flow, "MFCA3FuelFlow": rng.normal(0, 0.002, len(t)),
                       "PMT1": pmt, "PMT2": pmt * 0.5, "TCBurner": 1e-4 + np.where(t > 21, 1e-4 * np.minimum(t - 21, flame_end - 21), 0),
                       "PTA2": 1.0 + np.where(t > 21, 0.01, 0.0), "Radiometer3+30LoGain": rad, "Radiometer3+30HiGain": rad * 5,
                       "RadiometerOffset": 1.2})
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("2021-01-01 001 23:59:30:000 ,Experiment: 5,Test Point: 21001A1,MFCA1 Gas: 3\n")
        df.to_csv(fh, index=False)
    return path


def _features(path):
    meta, df = ts.parse_stream(path)
    return meta, ts.extract_features(meta, df)


def test_self_extinguished_flame_timeline(tmp_path):
    meta, f = _features(_write_stream(tmp_path / "PSI-159_Raw Data_21001A1_data.csv", flame_end=35.0))
    assert meta["Test Point"] == "21001A1" and f["sample_hz"] == pytest.approx(HZ, rel=0.01)
    assert f["record_s"] == pytest.approx(80, abs=0.1)  # the record crosses midnight
    assert f["t_flow_on_s"] == pytest.approx(20, abs=0.2) and f["t_flow_off_s"] == pytest.approx(60, abs=0.2)
    assert f["t_ignition_s"] == pytest.approx(21, abs=0.1) and f["flame_duration_s"] == pytest.approx(14, abs=0.2)
    assert f["ts_extinction_mode"] == "self_extinguished" and f["lead_before_flow_off_s"] == pytest.approx(25, abs=0.3)
    assert f["n_flame_segments"] == 1 and f["n_radiometers"] == 1  # lo-gain channel only; offset and hi-gain ignored


def test_flow_terminated_and_lights_are_not_a_flame(tmp_path):
    _, f = _features(_write_stream(tmp_path / "PSI-10_Raw Data_19001B2_data.csv", flame_end=60.05))
    assert f["ts_extinction_mode"] == "flow_terminated" and f["t_ignition_s"] == pytest.approx(21, abs=0.1)
    assert f["tc_burner_peak_at_flow_off"]


def test_priming_pulse_with_lights_on_is_not_the_test_flow(tmp_path):
    path = _write_stream(tmp_path / "PSI-159_Raw Data_21001D1_data.csv", flame_end=35.0)
    df = pd.read_csv(path, skiprows=1)
    t = np.arange(len(df)) / HZ
    df.loc[(t >= 5) & (t <= 5.4), "MFCA1StaticMixerFlow"] = 16.0  # tall, short priming spike while lights are on
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("2021-01-01 001 23:59:30:000 ,Experiment: 5,Test Point: 21001D1\n")
        df.to_csv(fh, index=False)
    _, f = _features(path)
    assert f["t_flow_on_s"] == pytest.approx(20, abs=0.2) and f["flame_duration_s"] == pytest.approx(14, abs=0.2)


def test_classify_flame_discounts_igniter_glow():
    assert ts.classify_flame(np.nan, 3.0) == "none"
    assert ts.classify_flame(3.4, 3.0) == "transient" and ts.classify_flame(11.0, 10.0) == "transient"
    assert ts.classify_flame(13.0, 3.0) == "sustained" and ts.classify_flame(6.0, None) == "sustained"


def test_oscillation_lead_measures_the_final_oscillating_stretch(tmp_path):
    _, calm = _features(_write_stream(tmp_path / "a_data.csv", flame_end=40.0))
    _, osc = _features(_write_stream(tmp_path / "b_data.csv", flame_end=40.0, oscillate=True))
    assert calm["rad_osc_lead_s"] < 0.5 and osc["rad_osc_lead_s"] == pytest.approx(4.0, abs=1.0)


def test_no_flame_gives_nan_not_zero(tmp_path):
    path = _write_stream(tmp_path / "PSI-159_Raw Data_21001C1_data.csv", flame_end=0.0)
    _, f = _features(path)
    assert not f["flame_seen"] and np.isnan(f["flame_duration_s"]) and f["ts_extinction_mode"] is None
    assert np.isnan(f["rad_peak_v"])


def test_oscillation_index_detects_pre_extinction_oscillation(tmp_path):
    _, calm = _features(_write_stream(tmp_path / "a_data.csv", flame_end=40.0))
    _, osc = _features(_write_stream(tmp_path / "b_data.csv", flame_end=40.0, oscillate=True))
    assert osc["rad_osc_rms_rel"] > 5 * calm["rad_osc_rms_rel"]
    assert osc["rad_osc_freq_hz"] == pytest.approx(2.0, abs=0.4)


def test_script_log_and_config_are_joined(tmp_path):
    folder = tmp_path / "PSI-10"
    folder.mkdir()
    _write_stream(folder / "PSI-10_Raw Data_19001B2_data.csv", flame_end=35.0)
    (folder / "PSI-10_Raw Data_19001B2_TP.txt").write_text(
        "Test Point: 19001B2\n\nIgnition and retraction: 2019-04-25 19:21:34\nMFCs off: 2019-04-25 19:22:19\n"
        "Extinction detected: 2019-04-25 19:22:11\nPreheat igniter: ***\n", encoding="utf-8")
    (folder / "PSI-10_Raw Data_19001B2.txt").write_text(
        "testpointName:19001B2,\nflowTimeoutSec:175,\nigniterIgnitionPowerV:3.75,\nextinctionDetectionStopsTest:true,\n",
        encoding="utf-8")
    (folder / "PSI-10_Raw Data_19001B2_Comments.txt").write_text("hit burner T limit\n", encoding="utf-8")
    row = ts.build_features(tmp_path, tmp_path / "out.parquet").iloc[0]
    assert row.tp_ignition_to_extinction_s == 37 and row.tp_extinction_to_mfcs_off_s == 8 and row.tp_extinction_logged
    assert row.cfg_flow_timeout_s == 175 and row.cfg_igniter_power_v == 3.75 and row.cfg_extinction_stops_test
    assert row.operator_comments == "hit burner T limit" and pd.isna(row.tp_mfcs_on)


def test_missing_logs_stay_missing(tmp_path):
    (tmp_path / "PSI-159").mkdir()
    _write_stream(tmp_path / "PSI-159" / "PSI-159_Raw Data_21001A1_data.csv", flame_end=35.0)
    row = ts.build_features(tmp_path, tmp_path / "out.parquet").iloc[0]
    assert row.tp_extinction_logged is None and pd.isna(row.cfg_flow_timeout_s) and row.operator_comments is None


def test_build_features_one_row_per_file_and_records_errors(tmp_path):
    (tmp_path / "PSI-159").mkdir()
    (tmp_path / "PSI-10").mkdir()
    _write_stream(tmp_path / "PSI-159" / "PSI-159_Raw Data_21001A1_data.csv", flame_end=35.0)
    (tmp_path / "PSI-10" / "PSI-10_Raw Data_19001B2_data.csv").write_text("broken\n", encoding="utf-8")
    (tmp_path / "PSI-10" / "PSI-10_Raw Data_19001B2_mfcSetpoints.csv").write_text("x\n", encoding="utf-8")
    table = ts.build_features(tmp_path, tmp_path / "out.parquet")
    assert list(table.test_id) == ["21001A1", "19001B2"] and table.parse_error.notna().tolist() == [False, True]
    assert (tmp_path / "out.parquet").exists()
