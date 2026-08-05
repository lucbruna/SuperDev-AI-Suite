"""Square layout — 1:1 general-purpose canvas."""
from __future__ import annotations

from typing import Any


class SquareLayout:
    """Defines the square 1:1 general-purpose canvas."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "square",
            "width": 1080,
            "height": 1080,
            "aspect_ratio": 1.0,
            "safe_area": {"left": 80, "right": 80, "top": 100, "bottom": 100},
            "max_frames": 50,
            "description": "Canvas quadrado genérico",
        }


_square_layout: SquareLayout | None = None


def get_square_layout() -> SquareLayout:
    global _square_layout
    if _square_layout is None:
        _square_layout = SquareLayout()
    return _square_layout
