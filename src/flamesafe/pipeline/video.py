"""ADR-0009 · Flame measurements from the ACME ops-camera video (CFI-G spherical flames).

One video = one test. Frames sampled at SAMPLE_FPS are reduced to the flame's equivalent radius, roundness, centre and the
mean brightness of the flame pixels (soot glow); a summary row per test gives durations and when the soot glow faded.
Thumbnails of the last lit frame (burner visible, for the pixel scale: burner diameter 6.35 mm) and of a steady flame are
kept for calibration and for the dashboard.

Runs locally or as a Cloud Run Job (`flamesafe video-task`, one task per manifest row). The video itself is downloaded
to a temporary file, measured and deleted: it is never stored. Outputs go to a local folder or a `gs://` prefix:

    <output>/frames/<test_id>.parquet     per-frame measurements
    <output>/summary/<test_id>.json       one summary row (includes provenance)
    <output>/thumbs/<test_id>_lit.jpg     last frame with the chamber lights on
    <output>/thumbs/<test_id>_flame.jpg   steady-flame frame

Brightness is in 8-bit camera units and is NOT comparable between tests (the ops-camera gain was adjusted at times).
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "-8")  # the downlink stream has benign decode warnings

BURNER_DIAMETER_MM = 6.35
LIGHTS_ON_MEAN = 60      # mean gray level with the chamber lights on (~104) vs dark (~4)
FLAME_LEVEL = 28         # 8-bit level separating flame from the dark background after a 5x5 blur
MIN_RADIUS_PX = 10       # below this it is sensor noise / hot pixels (~3.5 px)
GLARE_SAT_FRAC = 0.01    # thumbnail selection: prefer frames with <1 % saturated pixels
GLARE_WINDOW_S = 3.0     # igniter glare lasts the first seconds after the flame appears
HEAVY_SAT_FRAC = 0.10    # frames with >10 % saturated pixels are glare whatever the time
PERSIST_WINDOW_S = 1.0   # a flame must be detected in most frames of every second ...
PERSIST_FRACTION = 0.6   # ... (60 %), so sporadic spots after extinction do not extend it
PERSIST_GAP_S = 1.5      # dropouts shorter than this inside the flame are bridged
MIN_ROUNDNESS = 0.55     # below this the radius is flagged "check" (saturation, partial occlusion)
SAMPLE_FPS = 10.0        # frames measured per second of video (the source is ~30 fps)
BLANK_MAX_LEVEL = 20     # a frame whose brightest pixel stays below this carries no picture
EDGE_PX = 6              # border rows/columns ignored: the downlink adds a bright line on the top edge
TEST_ID = re.compile(r"(\d{5}[A-Z]\d+)")


def test_id_from_name(name: str) -> str | None:
    m = TEST_ID.search(name)
    return m.group(1) if m else None


class DecodeError(RuntimeError):
    """The decoder returned no usable picture (e.g. every frame blank)."""


def iter_frames(path: str | Path, sample_fps: float = SAMPLE_FPS):
    """Yield (t_seconds, BGR frame) sampled at `sample_fps`, decoded by the FFmpeg binary shipped with imageio-ffmpeg.

    OpenCV's own FFmpeg backend returned all-black frames for these H.264 downlink streams on Linux (Cloud Run,
    opencv-python-headless 5.0.0, 2026-11-16) while working on Windows; one decoder everywhere avoids that split.
    """
    import imageio_ffmpeg

    gen = imageio_ffmpeg.read_frames(str(path), pix_fmt="bgr24", output_params=["-vf", f"fps={sample_fps}"])
    meta = next(gen)
    w, h = meta["size"]
    for k, raw in enumerate(gen):
        yield k / sample_fps, np.frombuffer(raw, np.uint8).reshape(h, w, 3)


def measure_video(path: str | Path, sample_fps: float = SAMPLE_FPS) -> tuple[pd.DataFrame, dict[str, object]]:
    """Per-frame measurements and two thumbnails (JPEG bytes) for one video."""
    import cv2

    rows, n, informative, last_lit, best = [], 0, 0, None, (-1.0, None)
    for t, frame in iter_frames(path, sample_fps):
        n += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        informative += int(gray.max() > BLANK_MAX_LEVEL)
        lights = bool(gray.mean() > LIGHTS_ON_MEAN)
        row = {"t_s": t, "lights": lights, "sat_frac": float((gray >= 250).mean()), "r_eq_px": np.nan,
               "roundness": np.nan, "cx_px": np.nan, "cy_px": np.nan, "brightness": np.nan}
        if lights:
            last_lit = frame
        else:
            level = cv2.GaussianBlur(frame.max(axis=2), (5, 5), 0)
            level[:EDGE_PX], level[-EDGE_PX:], level[:, :EDGE_PX], level[:, -EDGE_PX:] = 0, 0, 0, 0
            mask = cv2.morphologyEx((level > FLAME_LEVEL).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                r_eq = float(np.sqrt(cv2.contourArea(c) / np.pi))
                if r_eq >= MIN_RADIUS_PX:
                    (cx, cy), r_enc = cv2.minEnclosingCircle(c)
                    inside = np.zeros_like(mask)
                    cv2.drawContours(inside, [c], -1, 1, -1)
                    bright = float(level[inside > 0].mean())
                    row |= {"r_eq_px": r_eq, "roundness": r_eq / r_enc if r_enc else np.nan, "cx_px": float(cx),
                            "cy_px": float(cy), "brightness": bright}
                    if row["sat_frac"] < GLARE_SAT_FRAC and bright > best[0]:
                        best = (bright, frame)
        rows.append(row)
    if n == 0 or informative < 0.05 * n:
        raise DecodeError(f"{path}: {informative} of {n} sampled frames carry any picture")
    frames = pd.DataFrame(rows)
    frames.attrs |= {"fps": sample_fps, "frames_read": n}
    thumbs = {}
    for key, img in (("lit", last_lit), ("flame", best[1])):
        if img is not None:
            ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ok:
                thumbs[key] = buf.tobytes()
    return frames, thumbs


def flame_window(frames: pd.DataFrame) -> tuple[float, float] | None:
    """Start and end of the flame: the longest stretch where the flame is detected in most frames of every second.

    Sporadic small spots (e.g. the burner still glowing after extinction, or noise) do not extend the flame.
    """
    if frames.empty or frames.r_eq_px.notna().sum() == 0:
        return None
    fps = frames.attrs.get("fps") or 1 / np.median(np.diff(frames.t_s))
    n = max(int(round(fps * PERSIST_WINDOW_S)), 1)
    seen = frames.r_eq_px.notna().astype(float)
    dense = (seen.rolling(n, center=True, min_periods=1).mean() >= PERSIST_FRACTION) & seen.astype(bool)
    t = frames.t_s.to_numpy()
    runs: list[list[float]] = []
    for ti, on in zip(t, dense.to_numpy(), strict=True):
        if not on:
            continue
        if runs and ti - runs[-1][1] <= PERSIST_GAP_S:
            runs[-1][1] = ti
        else:
            runs.append([ti, ti])
    if not runs:
        return None
    a, b = max(runs, key=lambda r: r[1] - r[0])
    return (float(a), float(b)) if b > a else None


def summarize(frames: pd.DataFrame) -> dict[str, object]:
    """Durations, steady radius and soot-glow timing. Missing quantities are NaN, never 0."""
    out: dict[str, object] = {"fps": frames.attrs.get("fps", np.nan), "frames_read": frames.attrs.get("frames_read", 0),
                              "lights_off_s": np.nan, "flame_seen": False, "t_flame_on_s": np.nan,
                              "t_flame_off_s": np.nan, "flame_visible_s": np.nan, "r_steady_px": np.nan,
                              "r_max_steady_px": np.nan, "roundness": np.nan, "cx_px": np.nan, "cy_px": np.nan,
                              "glow_peak_after_on_s": np.nan, "glow_half_before_off_s": np.nan,
                              "r_change_last_5s_rel": np.nan, "radius_quality": None}
    if frames.empty:
        return out
    dark = frames[~frames.lights]
    out["lights_off_s"] = float(dark.t_s.min()) if len(dark) else np.nan
    window = flame_window(frames)
    if window is None:
        return out
    t_on, t_off = window
    flame = frames[frames.r_eq_px.notna() & frames.t_s.between(t_on, t_off)]
    # igniter glare: the first seconds after onset, or any heavily saturated frame
    steady = flame[(flame.t_s >= t_on + GLARE_WINDOW_S) & (flame.sat_frac < HEAVY_SAT_FRAC)]
    out |= {"flame_seen": True, "t_flame_on_s": t_on, "t_flame_off_s": t_off, "flame_visible_s": t_off - t_on}
    if len(steady):
        r = steady.set_index("t_s").r_eq_px.rolling(9, center=True, min_periods=1).median()
        b = steady.set_index("t_s").brightness.rolling(9, center=True, min_periods=1).median()
        out |= {"r_steady_px": float(steady.r_eq_px.median()), "r_max_steady_px": float(r.max()),
                "roundness": float(steady.roundness.median()), "cx_px": float(steady.cx_px.median()),
                "cy_px": float(steady.cy_px.median()), "glow_peak_after_on_s": float(b.idxmax() - t_on)}
        after = b[b.index > b.idxmax()]
        half = after[after < 0.5 * b.max()]
        if len(half):
            out["glow_half_before_off_s"] = float(t_off - half.index.min())
        late, mid = r[r.index >= t_off - 5], r[(r.index >= t_on + 5) & (r.index < t_off - 5)]
        if len(late) and len(mid):
            out["r_change_last_5s_rel"] = float(late.median() / mid.median() - 1)
    # the duration is robust; the radius needs a round, unsaturated flame (camera gain was sometimes very high)
    rnd = out["roundness"]
    out["radius_quality"] = "ok" if isinstance(rnd, float) and rnd >= MIN_ROUNDNESS else "check"
    return out


# --------------------------------------------------------------------------------------------- output (local or GCS)

@dataclass
class Output:
    """A local directory or a `gs://bucket/prefix` destination."""

    uri: str

    @property
    def is_gcs(self) -> bool:
        return self.uri.startswith("gs://")

    @staticmethod
    def _client():
        """Storage client. On Cloud Run the project comes from the metadata server; on a laptop, from
        $GOOGLE_CLOUD_PROJECT or configs/video_manifest.yaml::cloud.project."""
        from google.cloud import storage

        from flamesafe import config

        project = os.environ.get("GOOGLE_CLOUD_PROJECT") or config.load("video_manifest").get("cloud", {}).get("project")
        return storage.Client(project=project)

    def _blob(self, rel: str):
        bucket, _, prefix = self.uri[5:].partition("/")
        return self._client().bucket(bucket).blob(f"{prefix.rstrip('/')}/{rel}".lstrip("/"))

    def exists(self, rel: str) -> bool:
        return self._blob(rel).exists() if self.is_gcs else (Path(self.uri) / rel).exists()

    def write(self, rel: str, data: bytes, content_type: str) -> None:
        if self.is_gcs:
            self._blob(rel).upload_from_string(data, content_type=content_type)
        else:
            path = Path(self.uri) / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def list(self, rel_dir: str) -> list[str]:
        if self.is_gcs:
            bucket, _, prefix = self.uri[5:].partition("/")
            full = f"{prefix.rstrip('/')}/{rel_dir}".lstrip("/")
            return [b.name[len(full):].lstrip("/") for b in self._client().list_blobs(bucket, prefix=full)]
        folder = Path(self.uri) / rel_dir
        return sorted(p.name for p in folder.glob("*")) if folder.exists() else []

    def read(self, rel: str) -> bytes:
        return self._blob(rel).download_as_bytes() if self.is_gcs else (Path(self.uri) / rel).read_bytes()


def _parquet_bytes(df: pd.DataFrame) -> bytes:
    import io

    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    return buf.getvalue()


def process_file(psi_id: str, file_name: str, expected_bytes: int | None, output: Output, client=None,
                 local_path: Path | None = None, overwrite: bool = False) -> dict[str, object]:
    """Download (unless `local_path`), measure, write outputs and delete the temporary video. Idempotent."""
    test_id = test_id_from_name(file_name) or Path(file_name).stem
    key = Path(file_name).stem.split("____")[-1] if "____" in file_name else test_id  # keeps suffixes like _failed...
    if not overwrite and output.exists(f"summary/{key}.json"):
        return {"key": key, "action": "skipped"}
    tmp_dir = None
    try:
        if local_path is None:
            from flamesafe.ingestion.psi_client import PSIClient

            client = client or PSIClient()
            tmp_dir = tempfile.mkdtemp(prefix="flamesafe-video-")
            local_path = Path(tmp_dir) / Path(file_name).name
            res = client.download(psi_id, file_name, local_path)
            size, sha = res.bytes, res.sha256
        else:
            size, sha = local_path.stat().st_size, None
        frames, thumbs = measure_video(local_path)
        summary = {"psi_id": psi_id, "test_id": test_id, "video_key": key, "source_file": file_name, "bytes": size,
                   "expected_bytes": expected_bytes, "size_matches": expected_bytes is None or size == expected_bytes,
                   "sha256": sha, **summarize(frames)}
        output.write(f"frames/{key}.parquet", _parquet_bytes(frames.assign(video_key=key)), "application/octet-stream")
        for name, data in thumbs.items():
            output.write(f"thumbs/{key}_{name}.jpg", data, "image/jpeg")
        output.write(f"summary/{key}.json", json.dumps(summary, default=_json_default, indent=1).encode(),
                     "application/json")
        return {"key": key, "action": "processed", "flame_visible_s": summary["flame_visible_s"]}
    finally:
        if tmp_dir:
            for p in Path(tmp_dir).glob("*"):
                p.unlink(missing_ok=True)
            Path(tmp_dir).rmdir()


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return None if isinstance(o, np.floating) and np.isnan(o) else o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


def collect(output: Output) -> pd.DataFrame:
    """Gather every summary JSON into one table (one row per video)."""
    rows = [json.loads(output.read(f"summary/{name}")) for name in output.list("summary") if name.endswith(".json")]
    return pd.DataFrame(rows).sort_values("video_key").reset_index(drop=True) if rows else pd.DataFrame()
