"""Closing scene board — call to action wrap-up."""
from __future__ import annotations

from typing import Any


class ClosingScene:
    """Renders a closing board with a call to action."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "closing",
            "frame": scene.get("frame", 1),
            "cta": scene.get("cta", ""),
            "caption": scene.get("caption", ""),
            "style": "closing card with CTA",
            "duration": 2.5,
        }


_closing_scene: ClosingScene | None = None


def get_closing_scene() -> ClosingScene:
    global _closing_scene
    if _closing_scene is None:
        _closing_scene = ClosingScene()
    return _closing_scene
