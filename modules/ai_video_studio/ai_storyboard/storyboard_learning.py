"""Storyboard learning — records feedback and adjusts scene choices."""
from __future__ import annotations

from collections import Counter
from typing import Any


class StoryboardLearning:
    """Learns which scene types perform best based on feedback."""

    def __init__(self) -> None:
        self._feedback: list[dict[str, Any]] = []

    def record(self, scene_type: str, score: float) -> None:
        self._feedback.append({"scene_type": scene_type, "score": float(score)})

    def top_scene_types(self, limit: int = 3) -> list[tuple[str, float]]:
        totals: dict[str, float] = {}
        counts: Counter[str] = Counter()
        for entry in self._feedback:
            totals[entry["scene_type"]] = totals.get(entry["scene_type"], 0.0) + entry["score"]
            counts[entry["scene_type"]] += 1
        ranked = sorted(
            ((t, totals[t] / counts[t]) for t in totals),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return ranked[:limit]

    def recommend(self) -> str:
        ranked = self.top_scene_types(1)
        return ranked[0][0] if ranked else "presentation"

    def size(self) -> int:
        return len(self._feedback)


_storyboard_learning: StoryboardLearning | None = None


def get_storyboard_learning() -> StoryboardLearning:
    global _storyboard_learning
    if _storyboard_learning is None:
        _storyboard_learning = StoryboardLearning()
    return _storyboard_learning
