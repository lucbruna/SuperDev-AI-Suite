"""X (Twitter) export — landscape MP4 with faststart web playback."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine


def export_x(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export a 1920x1080 MP4 suitable for X/Twitter."""
    return export_engine.export_frames(
        frames,
        preset="x_twitter",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )
