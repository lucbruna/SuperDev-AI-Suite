"""MOV export — Apple ProRes master files for editing workflows."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine


def export_mov_prores(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export frames to a ProRes MOV master (yuv422p10le)."""
    return export_engine.export_frames(
        frames,
        profile="mov_prores",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )


def export_mov(
    frames: list[Any], output_path: str | Path, *, fps: int = 30, **kw: Any
) -> dict[str, Any]:
    return export_mov_prores(frames, output_path, fps=fps, **kw)
