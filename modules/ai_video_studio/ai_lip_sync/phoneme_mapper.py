"""Phoneme Mapper — text to a timed phoneme timeline."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_voice_studio.normalization.phoneme_generator import (
    text_to_phonemes,
    phoneme_duration,
)


def map_text_to_phonemes(text: str, *, duration: float | None = None,
                         speaking_rate: float = 1.0) -> list[dict[str, Any]]:
    """Return ``[{phoneme, start, end, index}]`` for the text.

    If ``duration`` is given, the phoneme timings are scaled to fit it.
    """
    phonemes = text_to_phonemes(text)
    if not phonemes:
        return []
    entries: list[dict[str, Any]] = []
    cursor = 0.0
    for i, phoneme in enumerate(phonemes):
        dur = phoneme_duration(phoneme, speaking_rate=speaking_rate)
        entries.append({"index": i, "phoneme": phoneme, "start": cursor, "end": cursor + dur})
        cursor += dur
    if duration and cursor > 0 and duration > 0:
        scale = duration / cursor
        for entry in entries:
            entry["start"] *= scale
            entry["end"] *= scale
    return entries


def phoneme_count(text: str) -> int:
    return len(text_to_phonemes(text))
