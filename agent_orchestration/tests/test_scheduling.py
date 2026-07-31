"""Tests for the scheduling/ subpackage (Volume 31, Fase 5)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_events import OrchestratorEventType
from agent_orchestration.orchestrator_models import (AgentCapability,
                                                     AgentProfile, AgentStatus,
                                                     AgentTask, Priority,
                                                     TaskStatus)
from agent_orchestration.scheduling import (PriorityQueue, ResourceAllocator,
                                            SchedulingEngine, TaskQueue)


def _task(task_id: str, **kwargs: Any) -> AgentTask:
    defaults: dict[str, Any] = {"title": f"Tarefa {task_id}"}
    defaults.update(kwargs)
    return AgentTask(task_id=task_id, **defaults)


def _agent(agent_id: str, capability: str = "criar",
           status: AgentStatus = AgentStatus.IDLE) -> AgentProfile:
    return AgentProfile(agent_id=agent_id, name=agent_id,
                        capabilities=[AgentCapability(name=capability)],
                        status=status)


class TestTaskQueue:
    def test_fifo_order(self):
        queue = TaskQueue()
        queue.enqueue(_task("a"))
        queue.enqueue(_task("b"))
        first = queue.dequeue()
        second = queue.dequeue()
        assert first is not None and first.task_id == "a"
        assert second is not None and second.task_id == "b"
        assert queue.dequeue() is None

    def test_peek_and_size(self):
        queue = TaskQueue()
        assert queue.empty() is True
        queue.enqueue(_task("a"))
        peeked = queue.peek()
        assert peeked is not None and peeked.task_id == "a"
        assert queue.size() == 1


class TestPriorityQueue:
    def test_orders_by_priority(self):
        queue = PriorityQueue()
        queue.enqueue(_task("low", priority=Priority.LOW))
        queue.enqueue(_task("crit", priority=Priority.CRITICAL))
        queue.enqueue(_task("high", priority=Priority.HIGH))
        order = []
        for _ in range(3):
            task = queue.dequeue()
            assert task is not None
            order.append(task.task_id)
        assert order == ["crit", "high", "low"]

    def test_marks_task_queued(self):
        queue = PriorityQueue()
        task = _task("a", status=TaskStatus.PENDING)
        queue.enqueue(task)
        assert task.status == TaskStatus.QUEUED

    def test_empty(self):
        assert PriorityQueue().dequeue() is None
        assert PriorityQueue().peek() is None


class TestResourceAllocator:
    def test_assigns_capable_agent(self):
        allocator = ResourceAllocator()
        task = _task("t1", title="criar relatorio")
        agent = allocator.assign(task, [_agent("a1")])
        assert agent is not None
        assert agent.agent_id == "a1"
        assert task.agent_id == "a1"
        assert allocator.load("a1") == 1

    def test_skips_busy_agents(self):
        allocator = ResourceAllocator()
        task = _task("t1", title="criar app")
        agent = allocator.assign(
            task, [_agent("a1", status=AgentStatus.BUSY)])
        assert agent is None
        assert task.agent_id == ""

    def test_skips_non_matching_capability(self):
        allocator = ResourceAllocator()
        task = _task("t1", title="analisar dados")
        agent = allocator.assign(task, [_agent("a1", capability="criar")])
        assert agent is None

    def test_load_cap_and_release(self):
        allocator = ResourceAllocator()
        task = _task("t1", title="criar sistema")
        agent = _agent("a1")
        allocator.assign(task, [agent])
        allocator.release("a1")
        assert allocator.load("a1") == 0
        assert allocator.summary()["assigned"] == 0


class TestSchedulingEngine:
    def test_enqueue_emits_event(self):
        engine = SchedulingEngine()
        seen: list[str] = []
        engine.events.on(OrchestratorEventType.TASK_QUEUED,
                         lambda payload: seen.append(payload["task_id"]))
        engine.enqueue(_task("t1"))
        assert seen == ["t1"]
        assert engine.metrics.snapshot()["counters"].get(
            "ao.tasks_queued") == 1

    def test_priority_and_fifo_next(self):
        engine = SchedulingEngine()
        engine.enqueue(_task("fifo"))
        engine.enqueue_priority(_task("prio", priority=Priority.HIGH))
        fifo = engine.next_task()
        prio = engine.next_priority()
        assert fifo is not None and fifo.task_id == "fifo"
        assert prio is not None and prio.task_id == "prio"

    def test_assign_and_pending(self):
        engine = SchedulingEngine()
        engine.enqueue(_task("t1"))
        assert engine.pending() == 1
        agent = engine.assign(_task("t2", title="criar algo"),
                              [_agent("a1")])
        assert agent is not None
        engine.release("a1")

    def test_stats(self):
        engine = SchedulingEngine()
        engine.enqueue(_task("t1"))
        stats = engine.stats()
        assert stats["pending"] == 1
        assert "metrics" in stats
