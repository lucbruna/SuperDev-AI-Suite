"""Credits scene board — end credits roll."""
from __future__ import annotations

from typing import Any


class CreditsScene:
    """Renders an end credits board."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "credits",
            "frame": scene.get("frame", 1),
            "names": scene.get("names", []),
            "caption": scene.get("caption", ""),
            "style": "rolling credits",
            "duration": 5.0,
        }


_credits_scene: CreditsScene | None = None


def get_credits_scene() -> CreditsScene:
    global _credits_scene
    if _credits_scene is None:
        _credits_scene = CreditsScene()
    return _credits_scene
