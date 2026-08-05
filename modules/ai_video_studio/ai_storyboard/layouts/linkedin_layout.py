"""LinkedIn layout — professional 1.91:1 feed canvas."""
from __future__ import annotations

from typing import Any


class LinkedinLayout:
    """Defines the LinkedIn 1.91:1 feed video canvas."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "linkedin",
            "width": 1200,
            "height": 628,
            "aspect_ratio": 1200 / 628,
            "safe_area": {"left": 60, "right": 60, "top": 40, "bottom": 80},
            "max_frames": 40,
            "description": "Vídeo corporativo para feed do LinkedIn",
        }


_linkedin_layout: LinkedinLayout | None = None


def get_linkedin_layout() -> LinkedinLayout:
    global _linkedin_layout
    if _linkedin_layout is None:
        _linkedin_layout = LinkedinLayout()
    return _linkedin_layout
