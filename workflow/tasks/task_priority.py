from __future__ import annotations

import heapq
from typing import Any

from .task import Task


class TaskPriorityQueue:
    """Priority queue for task execution ordering."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, Task]] = []
        self._counter = 0

    def enqueue(self, task: Task) -> None:
        heapq.heappush(self._heap, (-task.priority, self._counter, task))
        self._counter += 1

    def dequeue(self) -> Task | None:
        return heapq.heappop(self._heap)[2] if self._heap else None

    def peek(self) -> Task | None:
        return self._heap[0][2] if self._heap else None

    def size(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0
