"""Director learning — captures directorial preferences across projects."""
from __future__ import annotations

from typing import Any


class DirectorLearning:
    """Stores and applies learnings from past productions."""

    def __init__(self) -> None:
        self._lessons: list[dict[str, Any]] = []

    def record(self, lesson: dict[str, Any]) -> None:
        self._lessons.append(lesson)

    def recall(self, key: str = "") -> list[dict[str, Any]]:
        if not key:
            return list(self._lessons)
        return [item for item in self._lessons if key in item.get("tags", [])]

    def stats(self) -> dict[str, Any]:
        return {"lessons": len(self._lessons)}


_director_learning: DirectorLearning | None = None


def get_director_learning() -> DirectorLearning:
    global _director_learning
    if _director_learning is None:
        _director_learning = DirectorLearning()
    return _director_learning
