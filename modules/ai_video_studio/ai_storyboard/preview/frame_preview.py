"""Frame preview — renders a single frame preview."""
from __future__ import annotations

from typing import Any


class FramePreview:
    """Produces a preview descriptor for a single frame."""

    def render(self, board: dict[str, Any]) -> dict[str, Any]:
        return {
            "frame": board.get("frame", 1),
            "type": board.get("type", "board"),
            "title": board.get("title", ""),
            "caption": board.get("caption", ""),
            "style": board.get("style", ""),
            "duration": board.get("duration", 2.5),
        }


_frame_preview: FramePreview | None = None


def get_frame_preview() -> FramePreview:
    global _frame_preview
    if _frame_preview is None:
        _frame_preview = FramePreview()
    return _frame_preview
