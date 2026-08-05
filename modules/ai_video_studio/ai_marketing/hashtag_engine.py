"""Hashtag Engine — platform-aware hashtag suggestions.

Builds hashtag sets from the video topic plus per-platform base sets and
generic growth tags, deduplicated and capped at the requested count.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

_PLATFORM_TAGS: dict[str, list[str]] = {
    "instagram": ["#reels", "#explore", "#instagood", "#reelsinstagram", "#video"],
    "tiktok": ["#fyp", "#fy", "#tiktokbrasil", "#foryou", "#tiktok"],
    "x": ["#trending", "#video", "#watch"],
    "youtube": ["#shorts", "#video"],
    "linkedin": ["#video", "#content"],
}

_GROWTH_TAGS = ["#viral", "#parati", "#fy", "#fyp", "#explore", "#novidades"]

_STOPWORDS = {"o", "a", "os", "as", "de", "do", "da", "em", "com", "para", "que",
              "the", "and", "of", "in", "para", "um", "uma", "no", "na"}


def _topic_tags(topic: str) -> list[str]:
    words = [w.lower() for w in re.split(r"[^a-zA-Z0-9]+", topic) if len(w) > 2]
    unique: list[str] = []
    for word in words:
        if word not in _STOPWORDS and word not in unique:
            unique.append(word)
    return [f"#{word}" for word in unique[:5]]


def generate_hashtags(
    topic: str,
    *,
    platform: str = "all",
    count: int = 10,
    language: str = "pt",
) -> list[str]:
    """Return a deduplicated hashtag list for the platform (``all`` = every platform)."""
    if not topic or not topic.strip():
        raise ValidationError("Topic is required", field="topic")
    if count < 1:
        raise ValidationError("Hashtag count must be positive", field="count")
    if platform not in {"all", *_PLATFORM_TAGS}:
        raise ValidationError(f"Unknown platform: {platform}", field="platform")
    if language not in {"pt", "en"}:
        raise ValidationError(f"Unsupported language: {language}", field="language")

    base: list[str] = []
    if platform == "all":
        for tags in _PLATFORM_TAGS.values():
            base.extend(tags)
    else:
        base = list(_PLATFORM_TAGS[platform])
    base.extend(_GROWTH_TAGS)

    combined = _topic_tags(topic) + base
    result: list[str] = []
    for tag in combined:
        if tag not in result:
            result.append(tag)
        if len(result) >= count:
            break
    return result[:count]
