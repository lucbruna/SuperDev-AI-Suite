"""Voice Engine — orchestrates real TTS synthesis for the AI Voice Studio.

Pipeline: normalize text → emotion prosody → cache lookup → chained synthesis
(edge-tts → gTTS → pyttsx3 → local formant synthesizer) → stats. Output is a
real audio file (WAV/MP3) under ``modules/downloads/voice/``.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import os
from pathlib import Path

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_voice_studio.voice_cache import get_voice_cache
from modules.ai_video_studio.ai_voice_studio.voice_statistics import get_voice_statistics
from modules.ai_video_studio.ai_voice_studio.synthesis.tts_engine import TTSEngine
from modules.ai_video_studio.ai_voice_studio.synthesis.emotion_controller import emotion_prosody
from modules.ai_video_studio.ai_voice_studio.normalization.text_cleaner import normalize_text

logger = logging.getLogger(__name__)

_SYNC_BRIDGE = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="voice_async")

_ENGINE = None


def get_voice_engine() -> VoiceEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = VoiceEngine()
    return _ENGINE


class VoiceEngine:
    """Synthesizes voice audio end-to-end with real files as output."""

    def __init__(self) -> None:
        self.tts = TTSEngine()
        self.cache = get_voice_cache()
        self.stats = get_voice_statistics()

    # ── Sync entry point ──────────────────────────────────────────
    def synthesize(
        self,
        text: str,
        *,
        voice_id: str = "default",
        language: str = "en",
        emotion: str | None = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        output_path: str | None = None,
        use_cache: bool = True,
    ) -> dict:
        """Synthesize narration synchronously (thread-bridged when needed)."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(
                self.synthesize_async(
                    text, voice_id=voice_id, language=language, emotion=emotion,
                    speed=speed, pitch=pitch, output_path=output_path, use_cache=use_cache,
                )
            )
        return _SYNC_BRIDGE.submit(
            asyncio.run,
            self.synthesize_async(
                text, voice_id=voice_id, language=language, emotion=emotion,
                speed=speed, pitch=pitch, output_path=output_path, use_cache=use_cache,
            ),
        ).result()

    # ── Async entry point ─────────────────────────────────────────
    async def synthesize_async(
        self,
        text: str,
        *,
        voice_id: str = "default",
        language: str = "en",
        emotion: str | None = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        output_path: str | None = None,
        use_cache: bool = True,
    ) -> dict:
        if not text or not text.strip():
            raise ValidationError("Cannot synthesize empty text", field="text")

        cleaned = normalize_text(text, language=language)
        if emotion:
            prosody = emotion_prosody(emotion)
            speed *= prosody["rate"]
            pitch *= prosody["pitch"]

        cache_key = f"{voice_id}|{language}|{cleaned[:300]}|{speed:.3f}|{pitch:.3f}|{emotion or ''}"
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached and os.path.exists(cached["output_path"]):
                return cached

        if output_path:
            resolved = Path(output_path)
            if not resolved.is_absolute() and not resolved.parent.exists():
                resolved = get_subsystem_dir("voice") / resolved
            out_dir = resolved.parent
            out_path = str(resolved)
        else:
            out_dir = get_subsystem_dir("voice")
            out_path = str(unique_filename(out_dir, f"voice_{voice_id}", "mp3"))

        result = await self.tts.synthesize(
            cleaned,
            voice_id=voice_id,
            language=language,
            speed=speed,
            pitch=pitch,
            output_path=out_path,
        )
        payload = {
            "output_path": result["output_path"],
            "duration": result["duration"],
            "engine": result["engine"],
            "voice_id": voice_id,
            "language": language,
            "emotion": emotion,
            "bytes": int(os.path.getsize(result["output_path"])) if os.path.exists(result["output_path"]) else 0,
            "cached": False,
        }
        if use_cache:
            self.cache.put(cache_key, payload)
        self.stats.record(engine=result["engine"], language=language, duration=result["duration"])
        return payload

    def list_voices(self) -> list[dict]:
        """All available voices from the synthesis catalog and profiles."""
        return self.tts.list_voices()
