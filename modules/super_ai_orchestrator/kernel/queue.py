"""PriorityQueue — deterministic priority queue for tasks.

Ordering rule: higher priority first; ties broken by lower ``seq``
(submitted earlier first). This makes scheduling fully deterministic for a
given submission sequence.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any

from modules.super_ai_orchestrator.core.task import Task


@dataclass(slots=True)
class PriorityQueue:
    """A min-heap over ``(-priority, seq, task)``.

    Attributes:
        _heap: internal heap storage.
    """

    _heap: list[tuple[int, int, Task]] = field(default_factory=list)

    def push(self, task: Task) -> None:
        heapq.heappush(self._heap, (-task.priority, task.seq, task))

    def pop(self) -> Task | None:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[2]

    def peek(self) -> Task | None:
        if not self._heap:
            return None
        return self._heap[0][2]

    def remove(self, seq: int) -> Task | None:
        """Remove the task with the given seq (used by cancellation)."""
        for i, (_, s, task) in enumerate(self._heap):
            if s == seq:
                del self._heap[i]
                heapq.heapify(self._heap)
                return task
        return None

    def contains(self, seq: int) -> bool:
        return any(s == seq for _, s, _ in self._heap)

    def __len__(self) -> int:
        return len(self._heap)

    def tasks(self) -> tuple[Task, ...]:
        return tuple(task for _, _, task in self._heap)

    def clear(self) -> None:
        self._heap.clear()
