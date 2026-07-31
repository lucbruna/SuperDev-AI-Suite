from __future__ import annotations

from typing import Any


class Feedback:
    """Feedback system for agents."""

    def __init__(self) -> None:
        self._feedbacks: dict[str, list[dict[str, Any]]] = {}

    def give(self, target_id: str, source_id: str, rating: float, comment: str = "") -> None:
        if target_id not in self._feedbacks:
            self._feedbacks[target_id] = []
        self._feedbacks[target_id].append({"from": source_id, "rating": rating, "comment": comment})

    def get_feedback(self, target_id: str) -> list[dict[str, Any]]:
        return list(self._feedbacks.get(target_id, []))

    def average_rating(self, target_id: str) -> float:
        fb = self._feedbacks.get(target_id, [])
        if not fb:
            return 0.0
        return sum(f["rating"] for f in fb) / len(fb)

    def clear(self) -> None:
        self._feedbacks.clear()
