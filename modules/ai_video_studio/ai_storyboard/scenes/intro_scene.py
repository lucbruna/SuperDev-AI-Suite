"""Intro scene board — opening hook with title."""
from __future__ import annotations

from typing import Any


class IntroScene:
    """Renders an intro board with a hook line."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "intro",
            "frame": scene.get("frame", 1),
            "title": scene.get("title", "Intro"),
            "caption": scene.get("caption", ""),
            "style": "bold title card",
            "duration": 2.5,
        }


_intro_scene: IntroScene | None = None


def get_intro_scene() -> IntroScene:
    global _intro_scene
    if _intro_scene is None:
        _intro_scene = IntroScene()
    return _intro_scene
