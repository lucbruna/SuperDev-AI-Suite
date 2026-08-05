"""TikTok layout — vertical 9:16 with full-bleed canvas."""
from __future__ import annotations

from typing import Any


class TiktokLayout:
    """Defines the TikTok vertical 9:16 canvas."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "tiktok",
            "width": 1080,
            "height": 1920,
            "aspect_ratio": 9 / 16,
            "safe_area": {"left": 60, "right": 60, "top": 220, "bottom": 340},
            "max_frames": 45,
            "description": "Vertical para TikTok com UI-safe zones",
        }


_tiktok_layout: TiktokLayout | None = None


def get_tiktok_layout() -> TiktokLayout:
    global _tiktok_layout
    if _tiktok_layout is None:
        _tiktok_layout = TiktokLayout()
    return _tiktok_layout
