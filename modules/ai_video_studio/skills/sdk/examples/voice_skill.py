"""Example skill — voice narration via the Voice Studio TTS chain."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.services.voice_studio import VoiceStudioService


class VoiceSkill:
    """Example voice skill: synthesize narration from text."""

    skill_id = "voice_example"
    skill_name = "Voice Example"
    skill_version = "1.0.0"
    skill_description = "Example narration skill built on the Voice Studio."
    skill_category = "voice"
    skill_tags = ["example", "voice", "tts"]
    skill_permissions = ["voice:tts"]
    skill_metadata = {"timeout_s": 90.0}

    def __init__(self) -> None:
        self._voice = VoiceStudioService()

    async def __call__(
        self, text: str, *, voice_id: str = "default", language: str = "en"
    ) -> dict[str, Any]:
        return await self._voice.synthesize(text, voice_id=voice_id, language=language)
