"""Explanation scene board — diagram/step-by-step explanation."""
from __future__ import annotations

from typing import Any


class ExplanationScene:
    """Renders an explanation board with steps."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "explanation",
            "frame": scene.get("frame", 1),
            "title": scene.get("title", "How it works"),
            "steps": scene.get("steps", []),
            "caption": scene.get("caption", ""),
            "style": "diagram with numbered steps",
            "duration": 4.0,
        }


_explanation_scene: ExplanationScene | None = None


def get_explanation_scene() -> ExplanationScene:
    global _explanation_scene
    if _explanation_scene is None:
        _explanation_scene = ExplanationScene()
    return _explanation_scene
