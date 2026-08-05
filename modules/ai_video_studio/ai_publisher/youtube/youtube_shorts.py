"""YouTube Shorts — Shorts-specific upload constraints and metadata (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MAX_DURATION_SECONDS = 60
_RECOMMENDED_ASPECT = "9:16"


class YoutubeShorts:
    """Validate and prepare YouTube Shorts content."""

    def validate(self, *, duration_seconds: float = 0.0, aspect_ratio: str = "") -> dict:
        """Check a clip against Shorts constraints."""
        issues = []
        if duration_seconds > _MAX_DURATION_SECONDS:
            issues.append(f"Shorts must be under {_MAX_DURATION_SECONDS} seconds.")
        if aspect_ratio and aspect_ratio not in ("9:16", "vertical"):
            issues.append(f"Shorts should be vertical ({_RECOMMENDED_ASPECT}).")
        return {"valid": not issues, "issues": issues}

    def prepare_metadata(self, *, title: str, description: str = "", hashtags: list[str] | None = None) -> dict:
        """Build Shorts-friendly metadata (short title + hashtags)."""
        short_title = title[:100]
        tags = (hashtags or [])[:3]
        full_description = description or ""
        if tags and "#Shorts" not in full_description:
            full_description = f"{full_description}\n#Shorts {' '.join('#' + t for t in tags)}"
        return {"title": short_title, "description": full_description, "category": "shorts"}

    def stats(self) -> dict[str, float | str]:
        return {"max_duration_seconds": _MAX_DURATION_SECONDS, "recommended_aspect": _RECOMMENDED_ASPECT}


_SHORTS: YoutubeShorts | None = None


def get_youtube_shorts() -> YoutubeShorts:
    """Get the module-level singleton Shorts helper."""
    global _SHORTS
    if _SHORTS is None:
        _SHORTS = YoutubeShorts()
    return _SHORTS
