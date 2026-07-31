"""FIFO task queue (Volume 31)."""

from __future__ import annotations

from collections import deque

from agent_orchestration.orchestrator_models import AgentTask


class TaskQueue:
    """Simple FIFO queue of agent tasks."""

    def __init__(self) -> None:
        self._queue: deque[AgentTask] = deque()

    def enqueue(self, task: AgentTask) -> None:
        self._queue.append(task)

    def dequeue(self) -> AgentTask | None:
        return self._queue.popleft() if self._queue else None

    def peek(self) -> AgentTask | None:
        return self._queue[0] if self._queue else None

    def size(self) -> int:
        return len(self._queue)

    def empty(self) -> bool:
        return not self._queue

    def clear(self) -> None:
        self._queue.clear()

    def all(self) -> list[AgentTask]:
        return list(self._queue)
