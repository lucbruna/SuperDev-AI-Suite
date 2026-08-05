"""Pause Alignment — inserts natural pauses between dubbed lines."""
from __future__ import annotations

from typing import Any

# Longer sentences breathe more: pause grows with the previous line's length.
MAX_PAUSE = 0.45
MIN_PAUSE = 0.12


def pause_after(line_text: str, *, punctuation: str | None = None) -> float:
    """Recommended pause after a line (seconds)."""
    if punctuation is None:
        punctuation = line_text[-1] if line_text else ""
    length = len(line_text)
    base = MIN_PAUSE + min(MAX_PAUSE, length / 300.0)
    if punctuation in ".!?":
        base += 0.15
    elif punctuation in ",;:":
        base += 0.05
    return round(min(MAX_PAUSE + 0.2, base), 3)


def apply_pauses(layout: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add ``pause_after`` to each laid-out line (excluding the last)."""
    out: list[dict[str, Any]] = []
    for i, line in enumerate(layout):
        entry = dict(line)
        entry["pause_after"] = pause_after(line.get("text", "")) if i < len(layout) - 1 else 0.0
        out.append(entry)
    return out
