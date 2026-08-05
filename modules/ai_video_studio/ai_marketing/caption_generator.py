"""Caption Generator — platform-specific video captions.

Builds ready-to-post captions (YouTube description, Instagram/TikTok caption,
X post, LinkedIn post) from the video title, topic and keywords, honoring
each platform's character limit.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

_PLATFORM_SPECS: dict[str, dict[str, Any]] = {
    "youtube": {"label": "YouTube description", "max": 5000},
    "instagram": {"label": "Instagram caption", "max": 2200},
    "tiktok": {"label": "TikTok caption", "max": 2200},
    "x": {"label": "X post", "max": 280},
    "linkedin": {"label": "LinkedIn post", "max": 3000},
}

_HASHTAG_PLATFORMS = {"instagram", "tiktok", "x"}

_PHRASES: dict[str, dict[str, str]] = {
    "pt": {
        "hook": "Você já viu isso? 🎬",
        "body_prefix": "Confira:",
        "cta": "Curta, compartilhe e salve! 🔖",
    },
    "en": {
        "hook": "Have you seen this? 🎬",
        "body_prefix": "Check it out:",
        "cta": "Like, share and save! 🔖",
    },
}


def generate_caption(
    title: str,
    *,
    platform: str = "instagram",
    topic: str | None = None,
    keywords: list[str] | None = None,
    hook: str | None = None,
    cta: str | None = None,
    language: str = "pt",
) -> dict[str, Any]:
    """Generate a caption for one platform, trimmed to its character limit."""
    if not title or not title.strip():
        raise ValidationError("Video title is required", field="title")
    normalized = platform.lower()
    if normalized not in _PLATFORM_SPECS:
        raise ValidationError(f"Unknown platform: {platform}", field="platform")
    if language not in _PHRASES:
        raise ValidationError(f"Unsupported language: {language}", field="language")

    phrases = _PHRASES[language]
    lines = [hook or phrases["hook"], ""]
    if topic:
        lines.append(f"{phrases['body_prefix']} {title.strip()} — {topic}.")
    else:
        lines.append(f"{phrases['body_prefix']} {title.strip()}.")
    if keywords:
        lines.append("")
        lines.append("• " + " | ".join(keywords[:8]))
    lines.append("")
    lines.append(cta or phrases["cta"])

    caption = "\n".join(lines)
    limit = _PLATFORM_SPECS[normalized]["max"]
    if len(caption) > limit:
        caption = caption[: limit - 1].rstrip() + "…"

    if normalized in _HASHTAG_PLATFORMS and keywords:
        from modules.ai_video_studio.ai_marketing.hashtag_engine import generate_hashtags

        tags = generate_hashtags(topic or title, platform=normalized, count=5, language=language)
        caption = f"{caption}\n\n{' '.join(tags)}"

    return {
        "platform": normalized,
        "caption": caption,
        "character_count": len(caption),
        "character_limit": limit,
        "language": language,
    }
