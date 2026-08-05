"""Language Transfer — speaks a clone's prosody in another language.

A cloned prosody (rate/pitch/energy) is applied on top of the best native
voice for the target language, so the output keeps the speaker's character
while using correct pronunciation.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_voice_studio.synthesis.multilingual_tts import voice_for_language, is_supported


def transfer_language(prosody: dict, target_language: str) -> dict:
    """Return ``{voice_id, language, rate, pitch}`` for speaking in another language."""
    voice_id = voice_for_language(target_language)
    if not is_supported(target_language):
        voice_id = "default"
    return {
        "voice_id": voice_id,
        "language": target_language,
        "rate": float(prosody.get("rate", 1.0)),
        "pitch": float(prosody.get("pitch", 1.0)),
    }


def supported_languages() -> list[str]:
    from modules.ai_video_studio.ai_voice_studio.synthesis.multilingual_tts import list_languages

    return list_languages()
