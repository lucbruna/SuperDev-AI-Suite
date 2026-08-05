"""WebM export — VP9 video with Opus audio for the web."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine


def export_webm(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export frames to WebM (libvpx-vp9)."""
    return export_engine.export_frames(
        frames,
        profile="webm_vp9",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )
