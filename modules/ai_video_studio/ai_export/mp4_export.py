"""MP4 export — convenience wrapper for H.264/H.265 MP4 output."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine
from modules.ai_video_studio.ai_export.export_profiles import MP4_H264, MP4_H265


def export_mp4(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    codec: str = "libx264",
    crf: int = 18,
    progress=None,
) -> dict[str, Any]:
    """Export frames to MP4 (H.264 by default, ``libx265`` for H.265)."""
    return export_engine.export_frames(
        frames,
        profile="mp4_h265" if codec == "libx265" else "mp4_h264",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
        codec_override=codec,
    )


def export_h264(
    frames: list[Any], output_path: str | Path, *, fps: int = 30, **kw: Any
) -> dict[str, Any]:
    return export_mp4(frames, output_path, fps=fps, codec="libx264", **kw)


def export_h265(
    frames: list[Any], output_path: str | Path, *, fps: int = 30, **kw: Any
) -> dict[str, Any]:
    return export_mp4(frames, output_path, fps=fps, codec="libx265", **kw)


# Profile constants re-exported for convenience
PROFILES = {"h264": MP4_H264, "h265": MP4_H265}
