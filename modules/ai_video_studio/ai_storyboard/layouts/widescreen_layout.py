"""Widescreen layout — ultra-wide 21:9 canvas for presentations."""
from __future__ import annotations

from typing import Any


class WidescreenLayout:
    """Defines the ultra-wide 21:9 canvas."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "widescreen",
            "width": 2560,
            "height": 1080,
            "aspect_ratio": 21 / 9,
            "safe_area": {"left": 120, "right": 120, "top": 80, "bottom": 140},
            "max_frames": 70,
            "description": "Ultra-widescreen para projetos cinematográficos",
        }


_widescreen_layout: WidescreenLayout | None = None


def get_widescreen_layout() -> WidescreenLayout:
    global _widescreen_layout
    if _widescreen_layout is None:
        _widescreen_layout = WidescreenLayout()
    return _widescreen_layout
