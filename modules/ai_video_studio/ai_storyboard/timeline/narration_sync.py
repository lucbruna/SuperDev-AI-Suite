"""Narration sync — aligns narration lines to boards."""
from __future__ import annotations

from typing import Any


class NarrationSync:
    """Synchronizes narration text with storyboard boards."""

    def sync(self, boards: list[dict[str, Any]], narration: list[str]) -> list[dict[str, Any]]:
        for i, board in enumerate(boards):
            board["narration"] = narration[i] if i < len(narration) else ""
        return boards

    def estimate_words_per_board(self, boards: list[dict[str, Any]], wpm: int = 150) -> list[int]:
        return [max(1, int((b.get("duration", 2.5) / 60) * wpm)) for b in boards]


_narration_sync: NarrationSync | None = None


def get_narration_sync() -> NarrationSync:
    global _narration_sync
    if _narration_sync is None:
        _narration_sync = NarrationSync()
    return _narration_sync
