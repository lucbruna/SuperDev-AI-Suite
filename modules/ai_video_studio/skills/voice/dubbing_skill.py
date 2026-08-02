"""Dubbing skill — re-voice foreign-language dialogue into a target language.

Synthesizes the translated script with a target voice and attaches the
source script so downstream stages (subtitles, mux) can stay in sync.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.services.voice_studio import VoiceStudioService


class DubbingSkill:
    """Produce dubbed audio for a script in a target language and voice."""

    skill_id = "dubbing"
    skill_name = "Dubbing"
    skill_version = "1.0.0"
    skill_description = "Dubbed audio for a script using a target voice and language."
    skill_category = "voice"
    skill_tags = ["voice", "tts", "dubbing", "localization"]
    skill_permissions = ["voice:tts"]
    skill_metadata = {"timeout_s": 90.0}

    def __init__(self) -> None:
        self._voice = VoiceStudioService()

    async def __call__(
        self,
        script: str,
        *,
        voice_id: str = "default",
        language: str = "en",
        speed: float = 1.0,
        source_script: str | None = None,
    ) -> dict[str, Any]:
        """Synthesize the dubbed audio for ``script``.

        Returns the TTS result plus the scripts so callers can burn in the
        dub as a subtitle track.
        """
        audio = await self._voice.synthesize(
            script,
            voice_id=voice_id,
            language=language,
            speed=speed,
        )
        return {
            **audio,
            "script": script,
            "source_script": source_script or script,
        }
