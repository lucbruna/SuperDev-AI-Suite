"""Storyboard optimizer — trims frame counts, normalizes pacing and aspect ratio."""
from __future__ import annotations

from typing import Any


class StoryboardOptimizer:
    """Optimizes storyboard boards for pacing and layout fit."""

    DEFAULT_ASPECT = 16 / 9

    def optimize(self, boards: list[dict[str, Any]], layout: dict[str, Any]) -> list[dict[str, Any]]:
        aspect = layout.get("aspect_ratio", self.DEFAULT_ASPECT)
        max_frames = layout.get("max_frames", len(boards))
        optimized = boards[:max_frames]
        for board in optimized:
            board["aspect_ratio"] = aspect
            board.setdefault("duration", 2.5)
        return optimized

    def estimate_pacing(self, boards: list[dict[str, Any]]) -> dict[str, Any]:
        durations = [b.get("duration", 2.5) for b in boards]
        total = sum(durations)
        return {"total_duration": total, "avg_duration": total / max(len(durations), 1), "frame_count": len(boards)}


_storyboard_optimizer: StoryboardOptimizer | None = None


def get_storyboard_optimizer() -> StoryboardOptimizer:
    global _storyboard_optimizer
    if _storyboard_optimizer is None:
        _storyboard_optimizer = StoryboardOptimizer()
    return _storyboard_optimizer
