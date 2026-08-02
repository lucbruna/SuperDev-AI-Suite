"""AI Voice Studio — real text-to-speech synthesis.

Implements the "voice" pillar of the studio (blueprint Volume 4). It reuses
the platform's provider-config philosophy but, unlike chat LLMs, TTS here is
provided by lightweight engines that need no API key:

1. ``edge-tts`` (primary) — Microsoft Edge neural voices, multilingual,
   high quality, network required.
2. ``gTTS`` (fallback) — Google Translate TTS, network required.
3. ``pyttsx3`` (offline fallback) — local SAPI voices, no network.

Synthesis always writes a real audio file (``.mp3``/``.wav``) and returns its
path, probed duration, and the engine used. A narrator catalog maps friendly
voice ids to engine-specific voice names so callers (routes and pipelines)
never deal with engine details.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import tempfile
from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.core.exceptions import AIError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NarratorProfile:
    """A named, reusable narrator voice."""

    id: str
    name: str
    gender: str  # male | female | neutral
    language: str  # BCP-47, e.g. en-US
    edge_voice: str  # edge-tts voice name
    gtts_lang: str  # gTTS language code
    style: list[str] = field(default_factory=list)  # tags: documentary, corporate...
    description: str = ""


NARRATOR_CATALOG: list[NarratorProfile] = [
    NarratorProfile("aria", "Aria (en, expressive)", "female", "en-US", "en-US-AriaNeural", "en", ["corporate", "storytelling"], "Warm, expressive US female"),
    NarratorProfile("jenny", "Jenny (en, friendly)", "female", "en-US", "en-US-JennyNeural", "en", ["friendly", "tutorial"], "Friendly, approachable US female"),
    NarratorProfile("guy", "Guy (en, clear)", "male", "en-US", "en-US-GuyNeural", "en", ["narrative", "tech"], "Clear, confident US male"),
    NarratorProfile("sonia", "Sonia (en-GB, documentary)", "female", "en-GB", "en-GB-SoniaNeural", "en", ["documentary"], "Calm, authoritative UK female"),
    NarratorProfile("ryan", "Ryan (en-GB)", "male", "en-GB", "en-GB-RyanNeural", "en", ["news", "documentary"], "Newsreader-style UK male"),
    NarratorProfile("francisca", "Francisca (pt-BR)", "female", "pt-BR", "pt-BR-FranciscaNeural", "pt", ["corporate", "friendly"], "Natural Brazilian Portuguese female"),
    NarratorProfile("antonio", "Antonio (pt-BR)", "male", "pt-BR", "pt-BR-AntonioNeural", "pt", ["narrative", "corporate"], "Deep Brazilian Portuguese male"),
    NarratorProfile("yuki", "Yuki (ja)", "female", "ja-JP", "ja-JP-NanamiNeural", "ja", ["anime", "friendly"], "Soft Japanese female"),
    NarratorProfile("elena", "Elena (es)", "female", "es-ES", "es-ES-ElviraNeural", "es", ["corporate", "storytelling"], "Melodic Spanish female"),
    NarratorProfile("default", "Default (auto)", "neutral", "en-US", "en-US-AriaNeural", "en", [], "Engine default voice"),
]


def _lookup_voice(voice_id: str, language: str) -> NarratorProfile:
    voice_id = (voice_id or "default").lower()
    for p in NARRATOR_CATALOG:
        if p.id == voice_id:
            return p
    lang = (language or "en").lower()
    for p in NARRATOR_CATALOG:
        if p.language.lower().startswith(lang.split("-")[0]):
            return p
    return NARRATOR_CATALOG[-1]


class VoiceStudioService:
    """Synthesizes narration audio via chained TTS engines."""

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = output_dir or os.path.join(tempfile.gettempdir(), "avs_voice")

    def list_voices(self) -> list[dict[str, Any]]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "gender": p.gender,
                "language": p.language,
                "style": p.style,
                "description": p.description,
            }
            for p in NARRATOR_CATALOG
        ]

    def _out_path(self, text: str, voice_id: str, ext: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_]+", "_", text[:30]).strip("_") or "voice"
        return os.path.join(self.output_dir, f"{voice_id}_{safe}_{abs(hash((text, voice_id))) % 100000}.{ext}")

    async def synthesize(
        self,
        text: str,
        *,
        voice_id: str = "default",
        language: str = "en",
        speed: float = 1.0,
        pitch: float = 1.0,
        emotion: str | None = None,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Synthesize narration and return file metadata.

        Returns ``{"file_path", "duration", "engine", "success"}``. Raises
        ``AIError`` only if every engine fails.
        """
        if not text.strip():
            raise AIError("Cannot synthesize empty text", context={"error": "empty_text"})
        profile = _lookup_voice(voice_id, language)
        os.makedirs(self.output_dir, exist_ok=True)

        path = output_path or self._out_path(text, profile.id, "mp3")
        errors: list[str] = []

        # 1) edge-tts (primary, best quality)
        try:
            await self._synthesize_edge(text, profile, speed, pitch, path)
            duration = await self._probe_duration(path)
            logger.info("TTS via edge-tts: %s (%.2fs)", profile.id, duration)
            return self._result(path, duration, "edge-tts")
        except Exception as e:  # noqa: BLE001
            errors.append(f"edge-tts: {e}")
            logger.warning("edge-tts failed (%s), trying gTTS", e)

        # 2) gTTS (network fallback, single voice per language)
        try:
            wav_path = path.rsplit(".", 1)[0] + ".mp3"
            await self._synthesize_gtts(text, profile, wav_path)
            duration = await self._probe_duration(wav_path)
            logger.info("TTS via gTTS (%s, %.2fs)", profile.id, duration)
            return self._result(wav_path, duration, "gtts")
        except Exception as e:  # noqa: BLE001
            errors.append(f"gtts: {e}")
            logger.warning("gTTS failed (%s), trying pyttsx3", e)

        # 3) pyttsx3 (fully offline fallback)
        try:
            wav_path = path.rsplit(".", 1)[0] + ".wav"
            await self._synthesize_pyttsx3(text, wav_path, speed)
            duration = await self._probe_duration(wav_path)
            logger.info("TTS via pyttsx3 (%.2fs)", duration)
            return self._result(wav_path, duration, "pyttsx3")
        except Exception as e:  # noqa: BLE001
            errors.append(f"pyttsx3: {e}")

        raise AIError(
            "All TTS engines failed",
            context={"error": "tts_unavailable", "details": "; ".join(errors)},
        )

    # ── Engine implementations ─────────────────────────────────────

    async def _synthesize_edge(
        self,
        text: str,
        profile: NarratorProfile,
        speed: float,
        pitch: float,
        path: str,
    ) -> None:
        import edge_tts

        rate = f"{int(round((speed - 1.0) * 100)):+d}%" if abs(speed - 1.0) > 0.01 else "+0%"
        pitch_hz = f"{int(round((pitch - 1.0) * 100)):+d}Hz" if abs(pitch - 1.0) > 0.01 else "+0Hz"
        communicate = edge_tts.Communicate(
            text,
            voice=profile.edge_voice,
            rate=rate,
            pitch=pitch_hz,
        )
        await communicate.save(path)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            raise RuntimeError("edge-tts produced empty output")

    async def _synthesize_gtts(self, text: str, profile: NarratorProfile, path: str) -> None:
        await asyncio.to_thread(self._gtts_sync, text, profile.gtts_lang, path)

    def _gtts_sync(self, text: str, lang: str, path: str) -> None:
        from gtts import gTTS

        tts = gTTS(text=text, lang=lang)
        tts.save(path)

    async def _synthesize_pyttsx3(self, text: str, path: str, speed: float) -> None:
        await asyncio.to_thread(self._pyttsx3_sync, text, path, speed)

    def _pyttsx3_sync(self, text: str, path: str, speed: float) -> None:
        import pyttsx3

        engine = pyttsx3.init()
        try:
            engine.setProperty("rate", int(180 * speed))
            engine.save_to_file(text, path)
            engine.runAndWait()
        finally:
            engine.stop()

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    async def _probe_duration(path: str) -> float:
        """Return audio duration in seconds via ffprobe (0 on failure)."""
        try:
            from modules.ai_video_studio.render_engine import RenderEngine

            probe = await RenderEngine().probe(path)
            return round(probe.duration, 3)
        except Exception:  # noqa: BLE001
            return 0.0

    @staticmethod
    def _result(file_path: str, duration: float, engine: str) -> dict[str, Any]:
        return {
            "file_path": file_path,
            "duration": duration,
            "engine": engine,
            "success": True,
        }
