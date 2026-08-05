"""Sentence Alignment — maps translated sentences onto source line timings.

Translated lines rarely have the same length as the source, so their ideal
speech durations (reading-speed model) are scaled to the source line slots.
"""
from __future__ import annotations

from typing import Any

CHARS_PER_SECOND = 15.0


def estimate_duration(text: str) -> float:
    """Ideal spoken duration for a line (seconds)."""
    return max(0.4, len(text) / CHARS_PER_SECOND)


def align_sentences(source_slots: list[dict[str, Any]],
                    translated_lines: list[str]) -> list[dict[str, Any]]:
    """``source_slots``: ``[{start, end, text}]``; returns per-line layout.

    Each output line: ``{text, start, end, source_text}`` — the translated
    line scaled to fill its source slot while keeping natural pacing.
    """
    out: list[dict[str, Any]] = []
    for i, (slot, line) in enumerate(zip(source_slots, translated_lines, strict=False)):
        slot_duration = max(0.5, slot["end"] - slot["start"])
        ideal = estimate_duration(line)
        scale = min(2.0, max(0.5, slot_duration / ideal))
        duration = min(slot_duration, ideal * scale)
        out.append({
            "index": i,
            "text": line,
            "source_text": slot.get("text", ""),
            "start": slot["start"],
            "end": slot["start"] + duration,
            "duration": duration,
        })
    return out
