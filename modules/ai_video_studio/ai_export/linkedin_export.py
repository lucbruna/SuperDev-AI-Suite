"""LinkedIn export — landscape 1920x1080 H.264 (medium bitrate)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine


def export_linkedin(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export a LinkedIn-ready MP4."""
    return export_engine.export_frames(
        frames,
        preset="linkedin",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )
