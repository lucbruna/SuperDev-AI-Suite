"""Voice Manager — catalog, lookup and synthesis facade for the AI Voice Studio."""
from __future__ import annotations

from modules.ai_video_studio.ai_voice_studio.voice_engine import get_voice_engine
from modules.ai_video_studio.ai_voice_studio.voice_models import VoiceSpec
from modules.ai_video_studio.ai_voice_studio.profiles import build_catalog

_MANAGER = None


def get_voice_manager() -> VoiceManager:
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = VoiceManager()
    return _MANAGER


class VoiceManager:
    """Registry of voices plus a thin facade over the engine."""

    def __init__(self) -> None:
        self.engine = get_voice_engine()
        self._catalog: dict[str, VoiceSpec] = {v.id: v for v in build_catalog()}

    def list_voices(self) -> list[dict]:
        return [v.to_dict() for v in self._catalog.values()]

    def get_voice(self, voice_id: str) -> VoiceSpec | None:
        return self._catalog.get(voice_id)

    def resolve(self, voice_id: str, language: str) -> VoiceSpec:
        """Resolve a voice id, falling back to language match then default."""
        if voice_id in self._catalog:
            return self._catalog[voice_id]
        lang = language.lower().split("-")[0]
        for v in self._catalog.values():
            if v.language.lower().startswith(lang):
                return v
        return self._catalog.get("default") or next(iter(self._catalog.values()))

    def synthesize(self, text: str, *, voice_id: str = "default", language: str = "en",
                   emotion: str | None = None, speed: float = 1.0, pitch: float = 1.0,
                   output_path: str | None = None) -> dict:
        return self.engine.synthesize(
            text, voice_id=voice_id, language=language, emotion=emotion,
            speed=speed, pitch=pitch, output_path=output_path,
        )
