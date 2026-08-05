"""Presentation scene board — slides for the main message."""
from __future__ import annotations

from typing import Any


class PresentationScene:
    """Renders a presentation board for a key message."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "presentation",
            "frame": scene.get("frame", 1),
            "title": scene.get("title", "Point"),
            "bullet_points": scene.get("bullets", []),
            "caption": scene.get("caption", ""),
            "style": "slide with bullets",
            "duration": 3.0,
        }


_presentation_scene: PresentationScene | None = None


def get_presentation_scene() -> PresentationScene:
    global _presentation_scene
    if _presentation_scene is None:
        _presentation_scene = PresentationScene()
    return _presentation_scene
