"""Comparison scene board — before/after or side-by-side."""
from __future__ import annotations

from typing import Any


class ComparisonScene:
    """Renders a comparison board between two options."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "comparison",
            "frame": scene.get("frame", 1),
            "left": scene.get("left", ""),
            "right": scene.get("right", ""),
            "caption": scene.get("caption", ""),
            "style": "split screen comparison",
            "duration": 3.5,
        }


_comparison_scene: ComparisonScene | None = None


def get_comparison_scene() -> ComparisonScene:
    global _comparison_scene
    if _comparison_scene is None:
        _comparison_scene = ComparisonScene()
    return _comparison_scene
