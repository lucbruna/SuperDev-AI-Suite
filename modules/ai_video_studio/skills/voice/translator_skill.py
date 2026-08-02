"""Translator skill — LLM subtitle/dialogue translation with safe fallback.

Reuses ``SubtitleStudioService.translate`` so it never raises when no LLM
provider is configured (deterministic no-op fallback).
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService


class TranslatorSkill:
    """Translate subtitle/dialogue text into a target language."""

    skill_id = "translator"
    skill_name = "Translator"
    skill_version = "1.0.0"
    skill_description = "Translate subtitle or dialogue text to a target language (LLM with fallback)."
    skill_category = "voice"
    skill_tags = ["voice", "translation", "localization", "llm"]
    skill_permissions = ["ai:llm"]

    def __init__(self) -> None:
        self._subtitles = SubtitleStudioService()

    async def __call__(
        self,
        text: str,
        *,
        target_language: str,
        source_language: str | None = None,
    ) -> dict[str, Any]:
        """Translate ``text`` and return ``{"text", "engine"}`` (``llm``|``fallback``)."""
        result = await self._subtitles.translate(text, target_language)
        return {
            **result,
            "source_language": source_language,
            "target_language": target_language,
        }
