"""Marketing Engine — one-shot campaign generation.

Orchestrates captions, hashtags, content ideas and a publishing schedule for
a video, and writes a real campaign JSON document under
``modules/downloads/marketing/``.
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
from modules.ai_video_studio.ai_marketing.caption_generator import generate_caption
from modules.ai_video_studio.ai_marketing.hashtag_engine import generate_hashtags

logger = logging.getLogger(__name__)

_ALL_PLATFORMS = ["youtube", "instagram", "tiktok", "x", "linkedin"]

_SCHEDULE = {
    "youtube": "Publicar na semana do lançamento",
    "instagram": "Reels no dia 1, post estático no dia 3",
    "tiktok": "Publish dia 1 e repost dia 4",
    "x": "Thread no dia 1, destaques no dia 2",
    "linkedin": "Post profissional no dia 2",
}


class MarketingEngine:
    """Creates complete marketing campaigns for a video."""

    def create_campaign(
        self,
        title: str,
        *,
        topic: str | None = None,
        keywords: list[str] | None = None,
        platforms: list[str] | None = None,
        cta: str | None = None,
        brand_name: str | None = None,
        language: str = "pt",
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Generate captions, hashtags, ideas and a schedule; write campaign JSON."""
        if not title or not title.strip():
            raise ValidationError("Video title is required", field="title")
        if language not in {"pt", "en"}:
            raise ValidationError(f"Unsupported language: {language}", field="language")

        wanted = platforms or _ALL_PLATFORMS
        unknown = [p for p in wanted if p not in _ALL_PLATFORMS]
        if unknown:
            raise ValidationError(f"Unknown platforms: {unknown}", field="platforms")

        captions = {
            platform: generate_caption(
                title,
                platform=platform,
                topic=topic,
                keywords=keywords,
                cta=cta,
                language=language,
            )["caption"]
            for platform in wanted
        }
        hashtags = generate_hashtags(topic or title, count=12, language=language)
        ideas = self._content_ideas(title, topic)

        data = {
            "title": title.strip(),
            "topic": topic,
            "brand": brand_name,
            "language": language,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "captions": captions,
            "hashtags": hashtags,
            "content_ideas": ideas,
            "schedule": {platform: _SCHEDULE[platform] for platform in wanted},
        }

        out_dir = Path(output_path).parent if output_path else get_subsystem_dir("marketing")
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "campaign"
        out_path = Path(output_path) if output_path else unique_filename(out_dir, f"campaign_{slug}", "json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        data["output_path"] = str(out_path)
        data["output_bytes"] = out_path.stat().st_size
        logger.info("Campaign for %r written to %s", title, out_path)
        return data

    @staticmethod
    def _content_ideas(title: str, topic: str | None) -> list[dict[str, str]]:
        subject = topic or title
        return [
            {"format": "Reels", "angle": f"Mostre os bastidores de: {subject}", "duration": "30-45s"},
            {"format": "Carrossel", "angle": f"5 motivos para assistir: {subject}", "slides": "5-7"},
            {"format": "Short", "angle": f"Melhor cena de {subject} em 15 segundos", "duration": "15s"},
            {"format": "Stories", "angle": "Enquete: qual parte você quer ver primeiro?", "duration": "1 dia"},
        ]


_MARKETING_ENGINE: MarketingEngine | None = None


def get_marketing_engine() -> MarketingEngine:
    """Return the shared MarketingEngine singleton."""
    global _MARKETING_ENGINE
    if _MARKETING_ENGINE is None:
        _MARKETING_ENGINE = MarketingEngine()
    return _MARKETING_ENGINE
