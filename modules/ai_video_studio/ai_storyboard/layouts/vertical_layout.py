"""Vertical layout — 9:16 canvas for reels and shorts."""
from __future__ import annotations

from typing import Any


class VerticalLayout:
    """Defines the vertical 9:16 canvas for reels/shorts."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "vertical",
            "width": 1080,
            "height": 1920,
            "aspect_ratio": 9 / 16,
            "safe_area": {"left": 60, "right": 60, "top": 240, "bottom": 320},
            "max_frames": 40,
            "description": "Vertical para Reels e Shorts",
        }


_vertical_layout: VerticalLayout | None = None


def get_vertical_layout() -> VerticalLayout:
    global _vertical_layout
    if _vertical_layout is None:
        _vertical_layout = VerticalLayout()
    return _vertical_layout
