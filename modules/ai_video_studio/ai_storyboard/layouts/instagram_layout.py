"""Instagram layout — 1:1 feed post canvas."""
from __future__ import annotations

from typing import Any


class InstagramLayout:
    """Defines the Instagram square 1:1 canvas."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "instagram",
            "width": 1080,
            "height": 1080,
            "aspect_ratio": 1.0,
            "safe_area": {"left": 80, "right": 80, "top": 120, "bottom": 160},
            "max_frames": 30,
            "description": "Post quadrado para feed do Instagram",
        }


_instagram_layout: InstagramLayout | None = None


def get_instagram_layout() -> InstagramLayout:
    global _instagram_layout
    if _instagram_layout is None:
        _instagram_layout = InstagramLayout()
    return _instagram_layout
