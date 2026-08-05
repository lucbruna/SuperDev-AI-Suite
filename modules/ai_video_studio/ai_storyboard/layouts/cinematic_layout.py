"""Cinematic layout — widescreen film-style 16:9 canvas."""
from __future__ import annotations

from typing import Any


class CinematicLayout:
    """Defines the cinematic 16:9 storyboard canvas."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "cinematic",
            "width": 1920,
            "height": 1080,
            "aspect_ratio": 16 / 9,
            "safe_area": {"left": 120, "right": 120, "top": 90, "bottom": 120},
            "max_frames": 60,
            "description": "Filme widescreen clássico",
        }


_cinematic_layout: CinematicLayout | None = None


def get_cinematic_layout() -> CinematicLayout:
    global _cinematic_layout
    if _cinematic_layout is None:
        _cinematic_layout = CinematicLayout()
    return _cinematic_layout
