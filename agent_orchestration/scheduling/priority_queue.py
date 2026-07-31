"""Priority-ordered task queue (Volume 31)."""

from __future__ import annotations

import heapq

from agent_orchestration.orchestrator_models import AgentTask, TaskStatus
from agent_orchestration.orchestrator_protocols import now


class PriorityQueue:
    """Dequeues tasks ordered by priority rank, then enqueue time."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, float, AgentTask]] = []

    def enqueue(self, task: AgentTask) -> None:
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.QUEUED
        heapq.heappush(self._heap, (-task.priority.rank, now(), task))

    def dequeue(self) -> AgentTask | None:
        return heapq.heappop(self._heap)[2] if self._heap else None

    def peek(self) -> AgentTask | None:
        return self._heap[0][2] if self._heap else None

    def size(self) -> int:
        return len(self._heap)

    def empty(self) -> bool:
        return not self._heap

    def all(self) -> list[AgentTask]:
        return [task for _, _, task in sorted(self._heap)]
