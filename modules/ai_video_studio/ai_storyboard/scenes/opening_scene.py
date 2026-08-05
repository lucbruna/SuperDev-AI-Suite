"""Opening scene board — establishes context and setting."""
from __future__ import annotations

from typing import Any


class OpeningScene:
    """Renders an opening board establishing the setting."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "opening",
            "frame": scene.get("frame", 1),
            "title": scene.get("title", "Opening"),
            "setting": scene.get("setting", ""),
            "caption": scene.get("caption", ""),
            "style": "wide establishing shot",
            "duration": 3.0,
        }


_opening_scene: OpeningScene | None = None


def get_opening_scene() -> OpeningScene:
    global _opening_scene
    if _opening_scene is None:
        _opening_scene = OpeningScene()
    return _opening_scene
