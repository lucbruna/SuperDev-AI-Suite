"""Thumbnail preview — generates thumbnail descriptors for boards."""
from __future__ import annotations

from typing import Any


class ThumbnailPreview:
    """Produces thumbnail descriptors for boards."""

    def render(self, board: dict[str, Any]) -> dict[str, Any]:
        return {
            "frame": board.get("frame", 1),
            "type": board.get("type", "board"),
            "title": board.get("title", ""),
            "thumbnail": None,
        }

    def render_all(self, boards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.render(b) for b in boards]


_thumbnail_preview: ThumbnailPreview | None = None


def get_thumbnail_preview() -> ThumbnailPreview:
    global _thumbnail_preview
    if _thumbnail_preview is None:
        _thumbnail_preview = ThumbnailPreview()
    return _thumbnail_preview
