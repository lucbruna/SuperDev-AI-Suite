"""Presentation layout — 4:3 classic slide canvas."""
from __future__ import annotations

from typing import Any


class PresentationLayout:
    """Defines the classic 4:3 presentation canvas."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "presentation",
            "width": 1024,
            "height": 768,
            "aspect_ratio": 4 / 3,
            "safe_area": {"left": 64, "right": 64, "top": 48, "bottom": 80},
            "max_frames": 60,
            "description": "Slides clássicos 4:3",
        }


_presentation_layout: PresentationLayout | None = None


def get_presentation_layout() -> PresentationLayout:
    global _presentation_layout
    if _presentation_layout is None:
        _presentation_layout = PresentationLayout()
    return _presentation_layout
