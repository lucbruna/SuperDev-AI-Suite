"""Subtitle sync — generates subtitle cues from narration."""
from __future__ import annotations

from typing import Any


class SubtitleSync:
    """Produces subtitle cues aligned to board timing."""

    def build(self, boards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cues = []
        cursor = 0.0
        for board in boards:
            duration = board.get("duration", 2.5)
            text = board.get("narration", "")
            if text:
                cues.append({"start": cursor, "end": cursor + duration, "text": text})
            cursor += duration
        return cues


_subtitle_sync: SubtitleSync | None = None


def get_subtitle_sync() -> SubtitleSync:
    global _subtitle_sync
    if _subtitle_sync is None:
        _subtitle_sync = SubtitleSync()
    return _subtitle_sync
