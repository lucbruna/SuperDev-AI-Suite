"""HDR export — HDR10/HLG metadata and 10-bit encoding helpers.

FFmpeg must be present; otherwise falls back to a standard SDR export with
a tonemapped approximation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.ai_export.export_engine import export_engine


def build_hdr_command(
    output_path: str | Path,
    *,
    width: int,
    height: int,
    fps: int,
    master_display: str = (
        "G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)"
        "L(10000000,1)"
    ),
    max_content: str = "4000",
    max_fall: str = "400",
) -> list[str]:
    """Return a full ffmpeg command array for an HDR10 10-bit encode."""
    return [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb48le",
        "-s", f"{width}x{height}", "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx265", "-crf", "16", "-preset", "slow",
        "-pix_fmt", "yuv420p10le",
        "-color_primaries", "bt2020",
        "-color_trc", "smpte2084",
        "-colorspace", "bt2020nc",
        "-master-display", master_display,
        "-max-cll", f"{max_content},{max_fall}",
        str(output_path),
    ]


def tonemap_sdr(frame: np.ndarray, exposure: float = 0.6) -> np.ndarray:
    """Approximate an HDR-looking frame to SDR via exposure compression."""
    f = np.asarray(frame).astype(np.float32) / 255.0
    # Reinhard-like tonemap
    toned = f / (1.0 + f * (1.0 - exposure))
    return np.clip(toned * 255.0, 0, 255).astype(np.uint8)


def export_hdr(
    frames: list[np.ndarray],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
) -> dict[str, Any]:
    """Export 10-bit HDR10 (BT.2020/PQ) using libx265.

    When FFmpeg is unavailable, falls back to an SDR export of tonemapped
    frames.
    """
    import shutil

    if not shutil.which("ffmpeg"):
        return {
            **export_engine.export_frames(
                [tonemap_sdr(f) for f in frames],
                profile="mp4_h265",
                fps=fps,
                resolution=resolution,
                output_path=output_path,
            ),
            "hdr": False,
            "reason": "ffmpeg missing — tonemapped SDR fallback",
        }

    import subprocess

    from PIL import Image

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    first = np.asarray(frames[0], dtype=np.uint8)
    if resolution:
        first = np.asarray(Image.fromarray(first).resize(resolution, Image.LANCZOS))
    h, w = first.shape[:2]

    cmd = build_hdr_command(out, width=w, height=h, fps=fps)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None

    def _to_48(f: np.ndarray) -> np.ndarray:
        arr = np.asarray(f, dtype=np.uint8)
        if resolution and (arr.shape[1] != resolution[0] or arr.shape[0] != resolution[1]):
            arr = np.asarray(Image.fromarray(arr).resize(resolution, Image.LANCZOS))
        # rgb48le expects big-endian uint16 samples
        u16 = arr.astype(">u2") * 257
        return u16

    proc.stdin.write(_to_48(first).tobytes())
    for frame in frames[1:]:
        proc.stdin.write(_to_48(frame).tobytes())
    proc.stdin.close()
    _, stderr = proc.communicate(timeout=1200)
    if proc.returncode != 0:
        raise RuntimeError(f"HDR encode failed: {stderr.decode()[-800:]}")
    return {
        "output_path": str(out),
        "hdr": True,
        "transfer": "smpte2084",
        "primaries": "bt2020",
        "bit_depth": 10,
        "engine": "ffmpeg",
    }
