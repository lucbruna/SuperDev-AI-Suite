"""Instagram export — Reels (9:16) and Posts (1:1) presets."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine


def export_reel(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export an Instagram Reel (1080x1920 vertical by default)."""
    return export_engine.export_frames(
        frames,
        preset="instagram_reel",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )


def export_post(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export a square Instagram post (1080x1080 by default)."""
    return export_engine.export_frames(
        frames,
        preset="instagram_post",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )


def export_instagram(frames: list[Any], output_path: str | Path, *, mode: str = "reel", **kw: Any) -> dict[str, Any]:
    """Export Instagram content; ``mode`` in {'reel', 'post'}."""
    if mode == "post":
        return export_post(frames, output_path, **kw)
    return export_reel(frames, output_path, **kw)
