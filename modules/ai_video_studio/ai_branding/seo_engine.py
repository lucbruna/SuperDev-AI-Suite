"""SEO Engine — platform-specific SEO metadata for video content.

Generates titles, descriptions and tags per platform (YouTube, TikTok,
Instagram, X, LinkedIn) with per-platform character limits, and writes a
real JSON metadata document under ``modules/downloads/seo/``.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

logger = logging.getLogger(__name__)

_PLATFORMS: dict[str, dict[str, int]] = {
    "youtube": {"title_max": 100, "description_max": 5000, "tags_max": 500},
    "tiktok": {"title_max": 80, "description_max": 2200, "tags_max": 100},
    "instagram": {"title_max": 64, "description_max": 2200, "tags_max": 30},
    "x": {"title_max": 60, "description_max": 280, "tags_max": 5},
    "linkedin": {"title_max": 120, "description_max": 3000, "tags_max": 3},
}

_HASHTAG_PLATFORMS = {"tiktok", "instagram", "x"}

_PHRASES: dict[str, dict[str, str]] = {
    "pt": {
        "hook": "Confira o novo vídeo!",
        "body_prefix": "Neste vídeo:",
        "cta": "Curta, compartilhe e salve!",
    },
    "en": {
        "hook": "Check out the new video!",
        "body_prefix": "In this video:",
        "cta": "Like, share and save!",
    },
}

_TAG_STOPWORDS = {"o", "a", "os", "as", "de", "do", "da", "em", "com", "para", "que", "the", "and", "of", "in"}


def _keywords_from_topic(topic: str | None) -> list[str]:
    if not topic:
        return []
    words = [w.lower() for w in re.split(r"[^a-zA-Z0-9]+", topic) if len(w) > 2]
    return [w for w in words if w not in _TAG_STOPWORDS]


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "video"


def _tag_keywords(title: str, topic: str | None, keywords: list[str] | None) -> list[str]:
    merged: list[str] = []
    for source in (keywords or [], _keywords_from_topic(topic), [title]):
        for word in source:
            tag = word.strip().strip("#").lower()
            if tag and len(tag) >= 3 and tag not in merged:
                merged.append(tag)
    return merged[:20]


def _build_title(title: str, platform: str, limit: int) -> str:
    cleaned = title.strip()
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1].rstrip() + "…"


def _build_description(title: str, topic: str | None, keywords: list[str], platform: str, language: str) -> str:
    phrases = _PHRASES.get(language, _PHRASES["pt"])
    lines = [phrases["hook"], ""]
    if topic:
        lines.append(f"{phrases['body_prefix']} {title} — {topic}.")
    else:
        lines.append(f"{phrases['body_prefix']} {title}.")
    if keywords:
        lines.append("")
        lines.append("• " + " | ".join(keywords[:8]))
    lines.append("")
    lines.append(phrases["cta"])
    description = "\n".join(lines)
    limit = _PLATFORMS[platform]["description_max"]
    return description if len(description) <= limit else description[: limit - 1] + "…"


def generate_seo_metadata(
    title: str,
    *,
    topic: str | None = None,
    keywords: list[str] | None = None,
    platforms: list[str] | None = None,
    language: str = "pt",
    output_path: str | None = None,
) -> dict[str, Any]:
    """Generate SEO metadata for the requested platforms (all by default)."""
    if not title or not title.strip():
        raise ValidationError("Video title is required", field="title")
    if language not in _PHRASES:
        raise ValidationError(f"Unsupported language: {language}", field="language")

    wanted = platforms or list(_PLATFORMS)
    unknown = [p for p in wanted if p not in _PLATFORMS]
    if unknown:
        raise ValidationError(f"Unknown platforms: {unknown}", field="platforms")

    base_keywords = _tag_keywords(title, topic, keywords)
    per_platform: dict[str, dict[str, Any]] = {}
    for platform in wanted:
        spec = _PLATFORMS[platform]
        tags = [f"#{k}" for k in base_keywords[: spec["tags_max"] or 0]] if platform in _HASHTAG_PLATFORMS else []
        per_platform[platform] = {
            "title": _build_title(title, platform, spec["title_max"]),
            "description": _build_description(title, topic, base_keywords, platform, language),
            "tags": tags,
            "tag_count": len(tags),
            "title_length": min(len(title.strip()), spec["title_max"]),
        }

    data = {
        "title": title.strip(),
        "topic": topic,
        "language": language,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platforms": per_platform,
    }

    out_dir = Path(output_path).parent if output_path else get_subsystem_dir("seo")
    out_path = Path(output_path) if output_path else unique_filename(out_dir, f"seo_{_slugify(title)}", "json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    data["output_path"] = str(out_path)
    data["output_bytes"] = out_path.stat().st_size
    logger.info("SEO metadata for %r written to %s", title, out_path)
    return data
