"""YouTube layout — 16:9 with title bar and lower-third reserved space."""
from __future__ import annotations

from typing import Any


class YoutubeLayout:
    """Defines the YouTube 16:9 canvas with lower-third zone."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": "youtube",
            "width": 1920,
            "height": 1080,
            "aspect_ratio": 16 / 9,
            "safe_area": {"left": 80, "right": 80, "top": 90, "bottom": 200},
            "max_frames": 90,
            "description": "Vídeo para YouTube com zona de legenda inferior",
        }


_youtube_layout: YoutubeLayout | None = None


def get_youtube_layout() -> YoutubeLayout:
    global _youtube_layout
    if _youtube_layout is None:
        _youtube_layout = YoutubeLayout()
    return _youtube_layout
