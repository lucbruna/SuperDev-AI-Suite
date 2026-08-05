"""Storyboard preview — renders a preview manifest of the storyboard."""
from __future__ import annotations

from typing import Any


class StoryboardPreview:
    """Produces a preview manifest for the full storyboard."""

    def render(self, storyboard: dict[str, Any]) -> dict[str, Any]:
        boards = storyboard.get("boards", [])
        return {
            "name": storyboard.get("name", "storyboard"),
            "frame_count": len(boards),
            "layout": storyboard.get("layout", {}).get("name", "cinematic"),
            "timeline": storyboard.get("timeline", []),
            "preview_url": None,
        }


_storyboard_preview: StoryboardPreview | None = None


def get_storyboard_preview() -> StoryboardPreview:
    global _storyboard_preview
    if _storyboard_preview is None:
        _storyboard_preview = StoryboardPreview()
    return _storyboard_preview
