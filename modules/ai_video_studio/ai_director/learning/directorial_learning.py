"""Directorial learning — aggregates learning signals for the director."""
from __future__ import annotations

from typing import Any


class DirectorialLearning:
    """Collects and applies directorial learnings."""

    def __init__(self) -> None:
        self._learnings: list[dict[str, Any]] = []

    def add(self, learning: dict[str, Any]) -> None:
        self._learnings.append(learning)

    def all(self) -> list[dict[str, Any]]:
        return list(self._learnings)


_directorial_learning: DirectorialLearning | None = None


def get_directorial_learning() -> DirectorialLearning:
    global _directorial_learning
    if _directorial_learning is None:
        _directorial_learning = DirectorialLearning()
    return _directorial_learning
