"""YouTube Thumbnail — thumbnail spec and scoring for YouTube (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_STANDARD_SIZE = (1280, 720)


class YoutubeThumbnail:
    """Build and score YouTube thumbnail specs (1280x720)."""

    def spec(self, *, title: str = "", features: dict | None = None) -> dict:
        """Return a thumbnail specification for generation."""
        features = features or {}
        return {
            "size": list(_STANDARD_SIZE),
            "aspect_ratio": "16:9",
            "max_size_kb": 2048,
            "title": title[:60],
            "elements": {
                "face": bool(features.get("has_face", False)),
                "text": features.get("text", ""),
                "accent_color": features.get("accent_color", "#ff0033"),
            },
        }

    def score(self, *, features: dict) -> dict:
        """Score a thumbnail spec with YouTube-specific heuristics."""
        score = 0.0
        if features.get("has_face"):
            score += 30.0
        if features.get("contrast", 0) >= 0.35:
            score += 25.0
        text = features.get("text", "")
        if 3 <= len(text) <= 8:
            score += 25.0
        elif text:
            score += 10.0
        if features.get("brightness", 0.5) >= 0.4:
            score += 20.0
        overall = round(min(100.0, score), 1)
        return {"score": overall, "rating": "high" if overall >= 80 else "medium" if overall >= 55 else "low"}

    def stats(self) -> dict[str, list[int]]:
        return {"standard_size": list(_STANDARD_SIZE)}


_THUMBNAIL: YoutubeThumbnail | None = None


def get_youtube_thumbnail() -> YoutubeThumbnail:
    """Get the module-level singleton thumbnail helper."""
    global _THUMBNAIL
    if _THUMBNAIL is None:
        _THUMBNAIL = YoutubeThumbnail()
    return _THUMBNAIL
