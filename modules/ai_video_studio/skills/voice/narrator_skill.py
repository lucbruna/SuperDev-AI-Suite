"""Narrator skill — real narration audio via the Voice Studio TTS chain.

Wraps ``VoiceStudioService.synthesize`` so any skill-aware caller (engine,
pipeline, HTTP) can produce narration from plain text with a named voice.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.services.voice_studio import VoiceStudioService


class NarratorSkill:
    """Synthesize narration audio (edge-tts → gTTS → pyttsx3)."""

    skill_id = "narrator"
    skill_name = "Narrator"
    skill_version = "1.0.0"
    skill_description = "Narration audio synthesis via the Voice Studio TTS chain."
    skill_category = "voice"
    skill_tags = ["voice", "tts", "narration"]
    skill_permissions = ["voice:tts"]
    skill_metadata = {"timeout_s": 90.0}

    def __init__(self) -> None:
        self._voice = VoiceStudioService()

    async def __call__(
        self,
        text: str,
        *,
        voice_id: str = "default",
        language: str = "en",
        speed: float = 1.0,
        emotion: str | None = None,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Synthesize narration and return ``{"file_path", "duration", "engine"}``."""
        return await self._voice.synthesize(
            text,
            voice_id=voice_id,
            language=language,
            speed=speed,
            emotion=emotion,
            output_path=output_path,
        )
