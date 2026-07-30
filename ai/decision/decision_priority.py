from __future__ import annotations

from typing import Any


class DecisionPriority:
    """Priority management for queued decisions."""

    URGENT = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    DEFERRED = 10

    def __init__(self):
        self._priorities: dict[str, int] = {}

    def set(self, context_id: str, priority: int) -> None:
        self._priorities[context_id] = max(0, min(100, priority))

    def get(self, context_id: str) -> int:
        return self._priorities.get(context_id, self.NORMAL)

    def remove(self, context_id: str) -> bool:
        return self._priorities.pop(context_id, None) is not None

    def sorted_ids(self) -> list[str]:
        return sorted(self._priorities, key=self._priorities.get, reverse=True)

    def clear(self) -> None:
        self._priorities.clear()
