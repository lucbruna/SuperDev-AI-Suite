"""Regression tests for truthful TTS fallback and language-aware default voice."""
from __future__ import annotations

import asyncio

import pytest

from modules.ai_video_studio.ai_voice_studio.synthesis.tts_engine import TTSEngine
from modules.ai_video_studio.services.voice_studio import _lookup_voice


def test_formant_fallback_is_not_reported_as_spoken_narration(monkeypatch):
    class NetworkUnavailable:
        async def synthesize(self, *args, **kwargs):
            raise RuntimeError("network unavailable")

    monkeypatch.setattr(
        "modules.ai_video_studio.services.voice_studio.VoiceStudioService",
        NetworkUnavailable,
    )

    class FormantOnly:
        def synthesize(self, *args, **kwargs):
            return {"output_path": "effect.wav", "duration": 1.0, "engine": "formant"}

    engine = TTSEngine()
    engine.offline = FormantOnly()

    with pytest.raises(RuntimeError, match="not available|formant audio|speech voice"):
        asyncio.run(engine.synthesize("Olá, mundo", language="pt-BR"))


def test_real_offline_speech_engine_is_accepted(monkeypatch):
    class NetworkUnavailable:
        async def synthesize(self, *args, **kwargs):
            raise RuntimeError("network unavailable")

    monkeypatch.setattr(
        "modules.ai_video_studio.services.voice_studio.VoiceStudioService",
        NetworkUnavailable,
    )

    class LocalSpeech:
        def synthesize(self, *args, **kwargs):
            return {"output_path": "speech.wav", "duration": 1.2, "engine": "pyttsx3"}

    engine = TTSEngine()
    engine.offline = LocalSpeech()

    result = asyncio.run(engine.synthesize("Olá, mundo", language="pt-BR"))
    assert result["engine"] == "pyttsx3"
    assert result["duration"] > 0


def test_default_voice_respects_brazilian_portuguese():
    profile = _lookup_voice("default", "pt-BR")
    assert profile.id == "francisca"
    assert profile.language == "pt-BR"


def test_explicit_voice_id_is_preserved():
    profile = _lookup_voice("antonio", "pt-BR")
    assert profile.id == "antonio"
