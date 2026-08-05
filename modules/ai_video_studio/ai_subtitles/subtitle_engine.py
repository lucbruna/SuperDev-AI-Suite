"""Subtitle Engine — generates real subtitle files (SRT/VTT/ASS).

Inputs:
* a transcript (text) + duration — timed with the reading-speed model.
* an audio/video file — transcribed (whisper when available, else VAD).

Outputs a real subtitle file under ``modules/downloads/subtitles/``.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue
from modules.ai_video_studio.ai_subtitles.subtitle_generator import cues_from_text
from modules.ai_video_studio.ai_subtitles.subtitle_optimizer import optimize
from modules.ai_video_studio.ai_subtitles import (
    subtitle_export_srt,
    subtitle_export_vtt,
    subtitle_export_ass,
)
from modules.ai_video_studio.ai_subtitles.speech_recognition import transcribe

logger = logging.getLogger(__name__)

_SUBTITLE = None


def get_subtitle_engine() -> SubtitleEngine:
    global _SUBTITLE
    if _SUBTITLE is None:
        _SUBTITLE = SubtitleEngine()
    return _SUBTITLE


class SubtitleEngine:
    """Creates subtitle files from text or media."""

    def generate(
        self,
        text: str | None = None,
        *,
        media_path: str | None = None,
        duration: float | None = None,
        format: str = "srt",
        output_path: str | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Generate a subtitle file; returns ``{file_path, format, cues, ...}``."""
        fmt = format.lower().lstrip(".")
        if fmt not in {"srt", "vtt", "ass"}:
            raise ValidationError(f"Unsupported subtitle format: {format}", field="format")

        cues, engine, media_duration = self._build_cues(text, media_path, duration, language)

        out_dir = Path(output_path).parent if output_path else get_subsystem_dir("subtitles")
        out_path = output_path or str(unique_filename(out_dir, f"subtitles_{fmt}", fmt))

        exporters = {"srt": subtitle_export_srt, "vtt": subtitle_export_vtt,
                     "ass": subtitle_export_ass}
        result = exporters[fmt].export(cues, out_path)
        result["engine"] = engine
        result["source"] = "media" if media_path else "transcript"
        result["duration"] = media_duration or (cues[-1].end if cues else 0.0)
        return result

    def _build_cues(self, text, media_path, duration, language) -> tuple[list[SubtitleCue], str, float]:
        if text:
            duration = duration or self._estimate_duration(text)
            cues = cues_from_text(text, max(duration, 1.0))
            return optimize(cues), "reading_speed", duration

        if media_path and os.path.exists(media_path):
            result = transcribe(media_path, language=language)
            segments = result["segments"]
            if segments and all(s.get("text") for s in segments):
                cues = [SubtitleCue(i + 1, s["start"], s["end"], s["text"]) for i, s in enumerate(segments)]
            elif segments:
                # VAD segments without text — synthesize placeholder-free timing.
                cues = [SubtitleCue(i + 1, s["start"], s["end"], "") for i, s in enumerate(segments)]
            else:
                cues = []
            total = segments[-1]["end"] if segments else 0.0
            return cues, result["engine"], total

        raise ValidationError("Provide text or a valid media path", field="text")

    @staticmethod
    def _estimate_duration(text: str) -> float:
        """Estimate narration duration from character count (reading speed)."""
        return max(2.0, len(text) / 15.0)
