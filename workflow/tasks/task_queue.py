from __future__ import annotations

from collections import deque
from typing import Any

from .task import Task


class TaskQueue:
    """FIFO queue for task execution."""

    def __init__(self) -> None:
        self._queue: deque[Task] = deque()

    def enqueue(self, task: Task) -> None:
        self._queue.append(task)

    def enqueue_front(self, task: Task) -> None:
        self._queue.appendleft(task)

    def dequeue(self) -> Task | None:
        return self._queue.popleft() if self._queue else None

    def peek(self) -> Task | None:
        return self._queue[0] if self._queue else None

    def size(self) -> int:
        return len(self._queue)

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def clear(self) -> None:
        self._queue.clear()
