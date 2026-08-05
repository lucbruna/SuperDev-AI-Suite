"""TikTok export — vertical 1080x1920 H.264, optionally capped at 15/60 s."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine

MAX_REELS_SECONDS = 15  # short-form TikTok clips


def export_tiktok(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    max_seconds: int | None = MAX_REELS_SECONDS,
    progress=None,
) -> dict[str, Any]:
    """Export for TikTok. If ``max_seconds`` is set, frames beyond the
    duration cap are dropped (first N frames are kept)."""
    if max_seconds and fps > 0:
        cap = int(max_seconds * fps)
        frames = list(frames)[:cap]
    return export_engine.export_frames(
        frames,
        preset="tiktok",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )
