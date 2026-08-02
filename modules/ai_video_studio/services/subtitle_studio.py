"""Subtitle Studio — timed SRT generation and AI translation.

Implements the "subtitles" pillar of the studio (blueprint, accessibility
volume). Real timing is computed from per-scene text length and duration
using a reading-speed model, instead of the flat word-count estimate used by
the legacy route. Translation reuses the platform LLM client with a safe
deterministic fallback so the service never fails when no provider is set.
"""
from __future__ import annotations
import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Any

from modules.ai_video_studio.core.exceptions import AIError

logger = logging.getLogger(__name__)

# Reading-speed model: ~15 chars/second is comfortable for subtitles.
CHARS_PER_SECOND = 15.0
MIN_CUE_SECONDS = 1.0
MAX_CUE_SECONDS = 6.0
DEFAULT_MAX_CHARS_PER_LINE = 42


def _format_timestamp(seconds: float) -> str:
    """Format seconds as an SRT timestamp ``HH:MM:SS,mmm``."""
    ms_total = max(0, int(round(seconds * 1000)))
    h, rem = divmod(ms_total, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _chunk_text(text: str, max_chars: int) -> list[str]:
    """Split text into lines of at most ``max_chars`` characters at word gaps."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


@dataclass
class SubtitleCue:
    index: int
    start: float
    end: float
    text: str

    def to_srt(self) -> str:
        return (
            f"{self.index}\n"
            f"{_format_timestamp(self.start)} --> {_format_timestamp(self.end)}\n"
            f"{self.text}\n"
        )


def cues_for_scene(text: str, duration: float, start_offset: float = 0.0, max_chars: int = DEFAULT_MAX_CHARS_PER_LINE) -> list[SubtitleCue]:
    """Split a scene's narration into timed cues that cover the scene duration."""
    lines = _chunk_text(text, max_chars)
    if not lines:
        return []

    # Ideal cue duration from reading speed, clamped to sane bounds.
    ideal = [max(MIN_CUE_SECONDS, min(MAX_CUE_SECONDS, len(line) / CHARS_PER_SECOND)) for line in lines]
    total_ideal = sum(ideal)

    # Distribute the scene duration across cues proportionally to their ideal.
    scale = duration / total_ideal if total_ideal > 0 else 1.0
    cues: list[SubtitleCue] = []
    t = start_offset
    for i, (line, dur) in enumerate(zip(lines, ideal, strict=False)):
        cue_duration = max(MIN_CUE_SECONDS, min(MAX_CUE_SECONDS, dur * scale))
        cues.append(SubtitleCue(index=i + 1, start=t, end=t + cue_duration, text=line))
        t += cue_duration
    return cues


class SubtitleStudioService:
    """Generates SRT subtitle files from scene narration and translates text."""

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = output_dir or os.path.join(tempfile.gettempdir(), "avs_subtitles")

    def generate_srt(
        self,
        scenes: list[dict],
        *,
        output_path: str | None = None,
        max_chars: int = DEFAULT_MAX_CHARS_PER_LINE,
    ) -> dict[str, Any]:
        """Generate an SRT file from scene dicts (``text`` + ``duration``).

        Returns ``{"file_path", "cue_count", "duration", "success"}``.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        path = output_path or os.path.join(self.output_dir, "subtitles.srt")

        cues: list[SubtitleCue] = []
        offset = 0.0
        for scene in scenes:
            text = scene.get("text") or scene.get("script") or scene.get("description") or ""
            duration = float(scene.get("duration", 3.0))
            if text.strip():
                cues.extend(cues_for_scene(text, duration, start_offset=offset, max_chars=max_chars))
            offset += duration

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(c.to_srt() for c in cues))

        return {
            "file_path": path,
            "cue_count": len(cues),
            "duration": offset,
            "success": True,
        }

    @staticmethod
    def read_srt(path: str) -> str:
        with open(path, encoding="utf-8") as f:
            return f.read()

    async def translate(
        self,
        text: str,
        target_language: str,
        *,
        db=None,
    ) -> dict[str, Any]:
        """Translate subtitle text via the platform LLM, with a fallback.

        Falls back to a deterministic no-op (original text kept, marker added)
        when no provider is configured or the LLM call fails, so translation
        never raises. Returns ``{"text", "engine"}`` where engine is
        ``"llm"`` or ``"fallback"``.
        """
        if not text.strip():
            return {"text": text, "engine": "fallback"}

        try:
            from modules.ai_video_studio.services.ai_studio import LLMClient

            result = await LLMClient.generate(
                f"Translate the following subtitle text to {target_language}. "
                f"Reply with ONLY the translated text, no quotes or commentary:\n\n{text}",
                system="You are a professional subtitle translator. Preserve tone and length.",
                temperature=0.2,
                db=db,
            )
            translated = (result.get("content") or "").strip()
            if translated:
                return {"text": translated, "engine": "llm"}
        except AIError as e:
            logger.info("Subtitle translation fallback (no provider): %s", e)
        except Exception as e:  # noqa: BLE001
            logger.warning("Subtitle translation failed, using fallback: %s", e)

        return {"text": text, "engine": "fallback"}
