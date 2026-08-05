"""YouTube export — high-bitrate MP4/H.265 optimized for YouTube upload."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_export.export_engine import export_engine

DEFAULT_PRESETS = ["youtube_1080p", "youtube_4k"]


def export_youtube(
    frames: list[Any],
    output_path: str | Path,
    *,
    fps: int = 30,
    resolution: tuple[int, int] | None = None,
    title: str | None = None,
    description: str | None = None,
    progress=None,
) -> dict[str, Any]:
    """Export for YouTube (H.264 1080p default)."""
    result = export_engine.export_frames(
        frames,
        preset="youtube_1080p",
        fps=fps,
        resolution=resolution,
        output_path=output_path,
        progress=progress,
    )
    _write_metadata(output_path, title, description)
    return result


def export_youtube_4k(
    frames: list[Any], output_path: str | Path, *, fps: int = 60, progress=None
) -> dict[str, Any]:
    return export_engine.export_frames(
        frames, preset="youtube_4k", fps=fps, output_path=output_path, progress=progress
    )


def _write_metadata(
    output_path: str | Path, title: str | None, description: str | None
) -> None:
    if not title and not description:
        return
    out = Path(output_path)
    meta_path = out.with_suffix(".youtube.json")
    data: dict[str, Any] = {}
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    meta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
