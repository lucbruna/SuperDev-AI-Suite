"""Outro scene board — final frame with branding and subscribe cue."""
from __future__ import annotations

from typing import Any


class OutroScene:
    """Renders an outro board with branding."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "outro",
            "frame": scene.get("frame", 1),
            "brand": scene.get("brand", ""),
            "cue": scene.get("cue", "Subscribe for more"),
            "caption": scene.get("caption", ""),
            "style": "branded outro card",
            "duration": 3.0,
        }


_outro_scene: OutroScene | None = None


def get_outro_scene() -> OutroScene:
    global _outro_scene
    if _outro_scene is None:
        _outro_scene = OutroScene()
    return _outro_scene
