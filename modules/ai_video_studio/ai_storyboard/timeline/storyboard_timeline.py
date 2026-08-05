"""Storyboard timeline — sequences boards into a time-ordered track."""
from __future__ import annotations

from typing import Any


class StoryboardTimeline:
    """Builds a time-ordered timeline from storyboard boards."""

    def build(self, boards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        timeline = []
        cursor = 0.0
        for board in boards:
            duration = board.get("duration", 2.5)
            timeline.append({"frame": board.get("frame", 1), "start": cursor, "end": cursor + duration, "type": board.get("type", "board")})
            cursor += duration
        return timeline

    def total_duration(self, boards: list[dict[str, Any]]) -> float:
        return sum(b.get("duration", 2.5) for b in boards)


_storyboard_timeline: StoryboardTimeline | None = None


def get_storyboard_timeline() -> StoryboardTimeline:
    global _storyboard_timeline
    if _storyboard_timeline is None:
        _storyboard_timeline = StoryboardTimeline()
    return _storyboard_timeline
