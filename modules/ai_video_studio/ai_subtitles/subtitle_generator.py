"""Subtitle Generator — turns a transcript into timed cues.

Uses the same reading-speed model as ``services/subtitle_studio`` (≈15 chars
per second) and caps cue length for readability.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue

CHARS_PER_SECOND = 15.0
MIN_CUE_SECONDS = 1.0
MAX_CUE_SECONDS = 6.0
DEFAULT_MAX_CHARS = 42


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    """Wrap text into lines of at most ``max_chars`` at word gaps."""
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


def cues_from_text(text: str, duration: float, *, start_offset: float = 0.0,
                   max_chars: int = DEFAULT_MAX_CHARS) -> list[SubtitleCue]:
    """Split a narration block into timed cues covering ``duration``."""
    lines = chunk_text(text, max_chars)
    if not lines:
        return []
    ideal = [max(MIN_CUE_SECONDS, min(MAX_CUE_SECONDS, len(line) / CHARS_PER_SECOND)) for line in lines]
    total = sum(ideal)
    scale = duration / total if total > 0 else 1.0
    cues: list[SubtitleCue] = []
    t = start_offset
    for i, (line, dur) in enumerate(zip(lines, ideal, strict=False)):
        cue_duration = max(MIN_CUE_SECONDS, min(MAX_CUE_SECONDS, dur * scale))
        cues.append(SubtitleCue(index=i + 1, start=t, end=t + cue_duration, text=line))
        t += cue_duration
    return cues
