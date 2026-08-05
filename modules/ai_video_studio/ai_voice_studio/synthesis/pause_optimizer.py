"""Pause Optimizer — inserts natural pauses based on punctuation and length.

For the offline and streaming paths (which concatenate chunks) this computes
where pauses belong so narration sounds natural, rather than machine-gun.
"""
from __future__ import annotations

import re
from typing import Any

_SENTENCE_RE = re.compile(r"([^.!?…]+[.!?…]*)")


def sentence_pauses(text: str) -> list[dict[str, Any]]:
    """Return ``[{text, pause_after}]`` with punctuation-driven pauses."""
    segments: list[dict[str, Any]] = []
    for match in _SENTENCE_RE.finditer(text):
        sentence = match.group(1).strip()
        if not sentence:
            continue
        last = sentence[-1]
        if last in ".!?":
            pause = 0.32
        elif last in ",;:":
            pause = 0.18
        else:
            pause = 0.08
        segments.append({"text": sentence, "pause_after": pause})
    return segments


def total_pause_time(text: str) -> float:
    """Sum of pauses implied by the text's punctuation."""
    return sum(seg["pause_after"] for seg in sentence_pauses(text))
