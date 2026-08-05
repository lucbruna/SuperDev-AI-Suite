"""Subtitle Timeline — timing primitives shared by all exporters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def to_timestamp(seconds: float, *, sep: str = ",", with_ms: bool = True) -> str:
    """Format seconds as ``HH:MM:SS{sep}mmm`` (SRT uses ',', VTT uses '.')."""
    ms_total = max(0, int(round(seconds * 1000)))
    h, rem = divmod(ms_total, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    if with_ms:
        return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


@dataclass
class SubtitleCue:
    """One subtitle entry with absolute timing."""

    index: int
    start: float
    end: float
    text: str
    style: str = "default"

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "start": self.start, "end": self.end,
                "text": self.text, "style": self.style}


def shift_cues(cues: list[SubtitleCue], offset: float) -> list[SubtitleCue]:
    return [SubtitleCue(c.index, c.start + offset, c.end + offset, c.text, c.style) for c in cues]


def scale_cues(cues: list[SubtitleCue], factor: float) -> list[SubtitleCue]:
    if factor <= 0:
        return cues
    return [SubtitleCue(c.index, c.start * factor, c.end * factor, c.text, c.style) for c in cues]
