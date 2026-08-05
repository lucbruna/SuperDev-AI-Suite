"""Testimonial scene board — quote with attribution."""
from __future__ import annotations

from typing import Any


class TestimonialScene:
    """Renders a testimonial quote board."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "testimonial",
            "frame": scene.get("frame", 1),
            "quote": scene.get("quote", ""),
            "author": scene.get("author", ""),
            "caption": scene.get("caption", ""),
            "style": "quote card",
            "duration": 3.0,
        }


_testimonial_scene: TestimonialScene | None = None


def get_testimonial_scene() -> TestimonialScene:
    global _testimonial_scene
    if _testimonial_scene is None:
        _testimonial_scene = TestimonialScene()
    return _testimonial_scene
