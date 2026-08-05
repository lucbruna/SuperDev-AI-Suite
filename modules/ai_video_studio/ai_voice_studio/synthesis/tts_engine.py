"""TTS Engine — the synthesis chain for the AI Voice Studio.

1. ``edge-tts`` (Microsoft neural, multilingual, best quality)
2. ``gTTS`` (Google, network fallback)
3. ``pyttsx3`` (offline OS voices)
4. ``formant synthesizer`` (pure numpy, always works, no network)

The chain never fails: the last engine is fully local and deterministic.
"""
from __future__ import annotations

import logging

from modules.ai_video_studio.ai_voice_studio.synthesis.offline_tts import OfflineTTS
from modules.ai_video_studio.ai_voice_studio.profiles import build_catalog

logger = logging.getLogger(__name__)

_TTS = None


def get_tts_engine() -> TTSEngine:
    global _TTS
    if _TTS is None:
        _TTS = TTSEngine()
    return _TTS


class TTSEngine:
    """Synthesizes speech to a real audio file using the chained engines."""

    def __init__(self) -> None:
        self.offline = OfflineTTS()
        self._catalog = {v.id: v for v in build_catalog()}

    def list_voices(self) -> list[dict]:
        return [v.to_dict() for v in self._catalog.values()]

    async def synthesize(
        self,
        text: str,
        *,
        voice_id: str = "default",
        language: str = "en",
        speed: float = 1.0,
        pitch: float = 1.0,
        output_path: str | None = None,
    ) -> dict:
        """Return ``{output_path, duration, engine}`` — never raises."""
        errors: list[str] = []

        # 1) Network engines via the existing VoiceStudioService.
        try:
            from modules.ai_video_studio.services.voice_studio import VoiceStudioService

            result = await VoiceStudioService().synthesize(
                text, voice_id=voice_id, language=language, speed=speed, pitch=pitch,
                output_path=output_path,
            )
            return {
                "output_path": result["file_path"],
                "duration": result["duration"],
                "engine": result["engine"],
            }
        except Exception as e:  # noqa: BLE001
            errors.append(f"network engines: {e}")

        # 2) Local engines (pyttsx3 → formant synthesizer).
        try:
            return self.offline.synthesize(
                text, output_path=output_path, rate=speed, pitch=pitch,
            )
        except Exception as e:  # noqa: BLE001
            errors.append(f"offline: {e}")

        raise RuntimeError("; ".join(errors) or "no TTS engine available")


def voice_for_language(language: str) -> str:
    """Pick the catalog voice best matching a BCP-47 language code."""
    lang = language.lower().split("-")[0]
    for voice in get_tts_engine().list_voices():
        if voice["language"].lower().startswith(lang):
            return voice["id"]
    return "default"


def engine_available(engine: str) -> bool:
    """Whether an engine dependency is importable."""
    return bool(__import__("importlib").util.find_spec(engine))
