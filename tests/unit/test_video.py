"""ADR-0009: flame measurement on a synthetic video with a known timeline and radius."""

from __future__ import annotations

import json

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from flamesafe.pipeline import video  # noqa: E402

FPS = 30


def _write_video(path, radius_px=60, fade=False, shrink=False):
    """Lights on 0-5 s, dark, igniter glare 6-7 s, flame 7-20 s (centre 320,240), dark until 25 s."""
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (640, 480))
    for i in range(25 * FPS):
        t = i / FPS
        img = np.zeros((480, 640, 3), np.uint8)
        if t < 5:
            img[:] = 110
        elif 6 <= t < 7:
            cv2.circle(img, (320, 240), 120, (255, 255, 255), -1)  # glare, not lights
        elif 7 <= t < 20:
            r = radius_px if not (shrink and t > 17) else int(radius_px * 0.7)
            level = 200 if not (fade and t > 12) else max(60, int(200 - 40 * (t - 12)))
            cv2.circle(img, (320, 240), r, (level // 3, level // 2, level), -1)
        writer.write(img)
    writer.release()
    return path


def test_measure_and_summarize_known_flame(tmp_path):
    frames, thumbs = video.measure_video(_write_video(tmp_path / "PSI-159_Raw Data_vlc-record-x____21001A1.avi"))
    s = video.summarize(frames)
    assert s["lights_off_s"] == pytest.approx(5, abs=0.2)
    assert s["flame_seen"] and s["t_flame_on_s"] == pytest.approx(6, abs=0.2)
    assert s["t_flame_off_s"] == pytest.approx(20, abs=0.2)
    assert s["r_steady_px"] == pytest.approx(60, abs=3) and s["roundness"] > 0.95
    assert s["cx_px"] == pytest.approx(320, abs=2) and s["cy_px"] == pytest.approx(240, abs=2)
    assert set(thumbs) == {"lit", "flame"}


def test_glow_fading_and_shrinking_are_detected(tmp_path):
    s = video.summarize(video.measure_video(_write_video(tmp_path / "a.avi", fade=True, shrink=True))[0])
    assert s["glow_half_before_off_s"] == pytest.approx(5.5, abs=1.0)  # level falls below half ~3.5 s after 12 s
    assert s["r_change_last_5s_rel"] < -0.1
    steady = video.summarize(video.measure_video(_write_video(tmp_path / "b.avi"))[0])
    assert np.isnan(steady["glow_half_before_off_s"]) and abs(steady["r_change_last_5s_rel"]) < 0.05


def test_sporadic_glow_after_extinction_does_not_extend_the_flame(tmp_path):
    path = _write_video(tmp_path / "glow.avi")
    frames, _ = video.measure_video(path)
    # add sporadic small detections after the flame ends (burner glowing): one frame in every 15
    late = frames.t_s > 21
    frames.loc[late & (frames.index % 15 == 0), "r_eq_px"] = 11.0
    s = video.summarize(frames)
    assert s["t_flame_off_s"] == pytest.approx(20, abs=0.3) and s["flame_visible_s"] == pytest.approx(14, abs=0.4)


def _write_plain(path, seconds_lit, seconds_dark, top_line=False):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (640, 480))
    for i in range((seconds_lit + seconds_dark) * FPS):
        img = np.full((480, 640, 3), 110 if i < seconds_lit * FPS else 0, np.uint8)
        if top_line:
            img[:2, ::3] = 200  # downlink artefact on the top edge
        writer.write(img)
    writer.release()
    return path


def test_no_flame_is_nan_not_zero_and_edge_line_ignored(tmp_path):
    s = video.summarize(video.measure_video(_write_plain(tmp_path / "dark.avi", 2, 3, top_line=True))[0])
    assert not s["flame_seen"] and np.isnan(s["flame_visible_s"]) and np.isnan(s["r_steady_px"])


def test_blank_decode_is_an_error_not_a_measurement(tmp_path):
    with pytest.raises(video.DecodeError):
        video.measure_video(_write_plain(tmp_path / "black.avi", 0, 3))


def test_process_file_writes_outputs_and_is_idempotent(tmp_path):
    src = _write_video(tmp_path / "PSI-159_Raw Data_vlc-record-2021____21001A1.avi")
    out = video.Output(str(tmp_path / "out"))
    res = video.process_file("PSI-159", src.name, src.stat().st_size, out, local_path=src)
    assert res["action"] == "processed"
    summary = json.loads(out.read("summary/21001A1.json"))
    assert summary["test_id"] == "21001A1" and summary["size_matches"] and summary["flame_visible_s"] > 10
    assert out.exists("frames/21001A1.parquet") and out.exists("thumbs/21001A1_flame.jpg")
    assert video.process_file("PSI-159", src.name, None, out, local_path=src)["action"] == "skipped"
    table = video.collect(out)
    assert list(table.video_key) == ["21001A1"] and bool(table.flame_seen.iloc[0])


def test_process_file_deletes_downloaded_video(tmp_path):
    src = _write_video(tmp_path / "source.avi")

    class FakeClient:
        def download(self, psi_id, file_name, dest):
            dest.write_bytes(src.read_bytes())
            self.dest = dest
            return type("R", (), {"bytes": dest.stat().st_size, "sha256": "x"})()

    client = FakeClient()
    out = video.Output(str(tmp_path / "out"))
    video.process_file("PSI-159", "PSI-159_Raw Data_vlc-record-y____21002B1.avi", None, out, client=client)
    assert not client.dest.exists() and not client.dest.parent.exists()
    assert out.exists("summary/21002B1.json")
