"""Scheduling subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import AgentProfile, AgentTask
from agent_orchestration.scheduling.priority_queue import PriorityQueue
from agent_orchestration.scheduling.resource_allocator import ResourceAllocator
from agent_orchestration.scheduling.task_queue import TaskQueue


class SchedulingEngine:
    """Facade over queues and resource allocation."""

    def __init__(self, queue: TaskQueue | None = None,
                 priority_queue: PriorityQueue | None = None,
                 allocator: ResourceAllocator | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.queue = queue or TaskQueue()
        self.priority_queue = priority_queue or PriorityQueue()
        self.allocator = allocator or ResourceAllocator()
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()

    def enqueue(self, task: AgentTask) -> None:
        self.queue.enqueue(task)
        self.metrics.increment("ao.tasks_queued")
        self.events.publish(OrchestratorEventType.TASK_QUEUED,
                            {"task_id": task.task_id})

    def enqueue_priority(self, task: AgentTask) -> None:
        self.priority_queue.enqueue(task)
        self.metrics.increment("ao.tasks_queued")

    def next_task(self) -> AgentTask | None:
        return self.queue.dequeue()

    def next_priority(self) -> AgentTask | None:
        return self.priority_queue.dequeue()

    def assign(self, task: AgentTask,
               agents: list[AgentProfile]) -> AgentProfile | None:
        return self.allocator.assign(task, agents)

    def release(self, agent_id: str) -> None:
        self.allocator.release(agent_id)

    def pending(self) -> int:
        return self.queue.size() + self.priority_queue.size()

    def stats(self) -> dict[str, Any]:
        return {"pending": self.pending(),
                "allocator": self.allocator.summary(),
                "metrics": self.metrics.snapshot()["counters"]}
