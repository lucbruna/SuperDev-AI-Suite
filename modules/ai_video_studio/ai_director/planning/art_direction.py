"""Art direction — defines the visual language of the production."""
from __future__ import annotations

from typing import Any


class ArtDirection:
    """Defines color palette and visual style."""

    def build(self, vision: str = "clean, modern, objective") -> dict[str, Any]:
        return {
            "vision": vision,
            "palette": ["#1a1a2e", "#16213e", "#0f3460", "#e94560"],
            "typography": "sans-serif, high contrast",
            "mood": "confident",
        }


_art_direction: ArtDirection | None = None


def get_art_direction() -> ArtDirection:
    global _art_direction
    if _art_direction is None:
        _art_direction = ArtDirection()
    return _art_direction
