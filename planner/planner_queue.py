from __future__ import annotations

from collections import deque
from typing import Any


class PlannerQueue:
    """Queue for task execution."""

    def __init__(self):
        self._queue: deque[Any] = deque()
        self._priority_queue: list[tuple[int, Any]] = []

    def enqueue(self, item: Any, priority: int = 0) -> None:
        if priority > 0:
            self._priority_queue.append((priority, item))
            self._priority_queue.sort(key=lambda x: -x[0])
        else:
            self._queue.append(item)

    def dequeue(self) -> Any | None:
        if self._priority_queue:
            return self._priority_queue.pop(0)[1]
        return self._queue.popleft() if self._queue else None

    def peek(self) -> Any | None:
        if self._priority_queue:
            return self._priority_queue[-1][1]
        return self._queue[0] if self._queue else None

    def is_empty(self) -> bool:
        return len(self._queue) == 0 and len(self._priority_queue) == 0

    def size(self) -> int:
        return len(self._queue) + len(self._priority_queue)

    def clear(self) -> None:
        self._queue.clear()
        self._priority_queue.clear()
