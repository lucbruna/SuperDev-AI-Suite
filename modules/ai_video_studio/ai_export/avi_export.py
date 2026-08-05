"""AVI export — legacy DV AVI container (25 fps, PCM audio)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine


def export_avi(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 25,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export frames to a DV AVI file (legacy/archival)."""
    return export_engine.export_frames(
        frames,
        profile="avi_dv",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )
