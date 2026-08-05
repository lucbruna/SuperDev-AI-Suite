"""MKV export — Matroska container with H.264 video and AAC audio."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine


def export_mkv(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export frames to an MKV file."""
    return export_engine.export_frames(
        frames,
        profile="mkv_h264",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )
