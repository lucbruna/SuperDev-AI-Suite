"""OrchestrationKernel — deterministic scheduling, control and audit.

The kernel owns the lifecycle of every task:

- ``submit`` assigns a monotonic ``seq``, optionally dedupes, and queues the
  task (or parks it at the governance gate).
- ``tick`` processes a bounded number of work slices: it pulls the
  highest-priority task, marks it SCHEDULED and, if an executor is
  registered and concurrency allows, RUNNING, then executes it.
- ``cancel`` / ``pause`` / ``resume`` / ``rollback`` give deterministic
  control over the lifecycle.
- Every state change is recorded in the ``AuditTrail`` and published on the
  ``EventBus``.

The kernel is deterministic: for the same submission sequence and the same
executor, it always produces the same ordering and outcome. No clock, no
network, no LLM calls here.
"""
from __future__ import annotations

from typing import Any, Callable

from modules.super_ai_orchestrator.config import KernelConfig
from modules.super_ai_orchestrator.core.context import OrchestrationContext
from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.core.task import Task
from modules.super_ai_orchestrator.events import EventBus
from modules.super_ai_orchestrator.events.event import (
    KERNEL_DEDUPED,
    KERNEL_QUEUE_FULL,
    TASK_CANCELLED,
    TASK_CHECKPOINTED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_PAUSED,
    TASK_QUEUED,
    TASK_RESUMED,
    TASK_ROLLED_BACK,
    TASK_SCHEDULED,
    TASK_STARTED,
    TASK_SUBMITTED,
    TASK_WAITING_APPROVAL,
)
from modules.super_ai_orchestrator.kernel.audit import AuditTrail
from modules.super_ai_orchestrator.kernel.queue import PriorityQueue

Executor = Callable[[OrchestrationContext], dict[str, Any]]
Rollback = Callable[[OrchestrationContext], dict[str, Any] | None]


class QueueFullError(ValueError):
    """Raised when the kernel queue capacity is exhausted."""


class OrchestrationKernel:
    """Deterministic scheduling and control kernel.

    Attributes:
        config: kernel behaviour settings.
        event_bus: bus to publish lifecycle events on.
        audit: append-only audit trail.
        running_count: number of tasks currently executing.
        executor: registered execution callable (may be None).
        rollback_fn: registered rollback callable (may be None).
    """

    def __init__(
        self,
        config: KernelConfig | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self.config = config or KernelConfig()
        self.event_bus = event_bus or EventBus()
        self.audit = AuditTrail()
        self.executor: Executor | None = None
        self.rollback_fn: Rollback | None = None
        self.planner: Callable[[Task], Any] | None = None
        self._queue = PriorityQueue()
        self._waiting: list[Task] = []  # selected but not yet executed
        self._tasks: dict[int, Task] = {}  # seq -> task
        self._active_keys: set[tuple] = set()
        self._next_seq = 0
        self.running_count = 0

    # ------------------------------------------------------------------ #
    # Setup
    # ------------------------------------------------------------------ #
    def set_executor(self, executor: Executor | None) -> None:
        """Register (or clear) the execution callable used by ``tick``."""
        self.executor = executor

    def set_rollback(self, rollback_fn: Rollback | None) -> None:
        """Register (or clear) the rollback callable used on failed tasks."""
        self.rollback_fn = rollback_fn

    def set_planner(self, planner: Callable[[Task], Any] | None) -> None:
        """Register (or clear) the plan builder used for execution contexts.

        The callable receives the task and returns an iterable of plan
        steps (objects exposing ``to_dict()`` or plain dicts). The steps are
        attached to the ``OrchestrationContext`` so executors can follow
        them.
        """
        self.planner = planner

    # ------------------------------------------------------------------ #
    # Submission
    # ------------------------------------------------------------------ #
    def submit(self, task: Task) -> Task:
        """Submit a task: assign seq, dedupe, queue or gate it.

        Raises:
            QueueFullError: if the queue is at capacity.
            ValueError: if the task is not in PENDING state.
        """
        if task.status != TaskStatus.PENDING:
            raise ValueError(f"task must be PENDING to submit, got {task.status.value}")
        if task.priority < self.config.min_priority or task.priority > self.config.max_priority:
            raise ValueError(
                f"priority {task.priority} out of range "
                f"[{self.config.min_priority}, {self.config.max_priority}]"
            )

        key = task.key()
        if self.config.dedupe_enabled and key in self._active_keys:
            self._emit(KERNEL_DEDUPED, task, {"deduplicated": True})
            self.audit.record("deduped", task.seq, {"title": task.title})
            return self._find_active(key)

        task.seq = self._next_seq
        self._next_seq += 1
        self._tasks[task.seq] = task
        self._active_keys.add(key)
        self._emit(TASK_SUBMITTED, task)

        if self.config.governance_required:
            task.status = TaskStatus.WAITING_APPROVAL
            self._emit(TASK_WAITING_APPROVAL, task)
            self.audit.record("gated", task.seq, {"title": task.title})
            return task

        self._enqueue(task)
        return task

    def _enqueue(self, task: Task) -> None:
        if len(self._queue) >= self.config.queue_capacity:
            self._emit(KERNEL_QUEUE_FULL, task)
            raise QueueFullError(f"queue capacity {self.config.queue_capacity} reached")
        task.transition(TaskStatus.QUEUED)
        self._queue.push(task)
        self._emit(TASK_QUEUED, task)
        self.audit.record("enqueued", task.seq, {"title": task.title})

    # ------------------------------------------------------------------ #
    # Governance hand-off
    # ------------------------------------------------------------------ #
    def approve(self, task: Task) -> Task:
        """Admit a gated task into the queue."""
        if task.status != TaskStatus.WAITING_APPROVAL:
            raise ValueError(
                f"cannot approve task in state {task.status.value}"
            )
        self._enqueue(task)
        self.audit.record("approved", task.seq)
        return task

    def reject(self, task: Task, reason: str) -> Task:
        """Reject a gated task."""
        if task.status != TaskStatus.WAITING_APPROVAL:
            raise ValueError(f"cannot reject task in state {task.status.value}")
        task.reason = reason
        task.transition(TaskStatus.REJECTED)
        self._release(task)
        self.audit.record("rejected", task.seq, {"reason": reason})
        return task

    # ------------------------------------------------------------------ #
    # Scheduling
    # ------------------------------------------------------------------ #
    def tick(self, slices: int | None = None) -> int:
        """Process up to ``slices`` work slices (default from config).

        Each slice pulls the highest-priority task, marks it SCHEDULED and,
        if an executor is registered and concurrency allows, executes it.

        Returns:
            The number of slices processed.
        """
        limit = slices if slices is not None else self.config.slices_per_tick
        processed = 0
        for _ in range(limit):
            task = self._waiting.pop(0) if self._waiting else self._queue.pop()
            if task is None:
                break
            processed += 1
            if task.status == TaskStatus.QUEUED:
                task.transition(TaskStatus.SCHEDULED)
                self._emit(TASK_SCHEDULED, task)
                self.audit.record("scheduled", task.seq)
            if self.running_count >= self.config.max_concurrent or self.executor is None:
                self._waiting.append(task)
                continue
            self._execute(task)
        return processed

    def _execute(self, task: Task) -> None:
        task.transition(TaskStatus.RUNNING)
        self.running_count += 1
        self._emit(TASK_STARTED, task)
        self.audit.record("started", task.seq)
        try:
            context = self._build_context(task)
            result = self.executor(context)  # type: ignore[misc]
            task.result = result if isinstance(result, dict) else {"output": result}
            task.transition(TaskStatus.COMPLETED)
            self._emit(TASK_COMPLETED, task)
            self.audit.record("completed", task.seq)
        except Exception as exc:  # deterministic capture
            task.error = str(exc)
            task.transition(TaskStatus.FAILED)
            self._emit(TASK_FAILED, task)
            self.audit.record("failed", task.seq, {"error": task.error})
            if self.config.rollback_on_failure:
                self.rollback(task)
        finally:
            self.running_count -= 1
        self._release(task)

    def _build_context(self, task: Task) -> OrchestrationContext:
        context = OrchestrationContext(task=task)
        if self.planner is not None:
            steps = self.planner(task)
            context.plan = tuple(
                step.to_dict() if hasattr(step, "to_dict") else step
                for step in steps
            )
        if task.checkpoint:
            context.restore(task.checkpoint)
        return context

    # ------------------------------------------------------------------ #
    # Control
    # ------------------------------------------------------------------ #
    def cancel(self, task: Task) -> Task:
        """Cancel a task that is not running.

        Valid for PENDING, WAITING_APPROVAL, QUEUED, APPROVED, SCHEDULED
        and PAUSED tasks.
        """
        if task.status == TaskStatus.RUNNING:
            raise ValueError("cannot cancel a running task synchronously")
        if task.status in TaskStatus.terminal():
            raise ValueError(f"task already terminal ({task.status.value})")
        if task.status == TaskStatus.SCHEDULED and task in self._waiting:
            self._waiting.remove(task)
        elif task.status == TaskStatus.QUEUED:
            self._queue.remove(task.seq)
        task.reason = "cancelled"
        task.transition(TaskStatus.CANCELLED)
        self._release(task)
        self._emit(TASK_CANCELLED, task)
        self.audit.record("cancelled", task.seq)
        return task

    def pause(self, task: Task, context: OrchestrationContext | None = None) -> Task:
        """Pause a scheduled task and persist a checkpoint.

        Valid from SCHEDULED (waiting for execution). The current context
        snapshot is stored as the task checkpoint so ``resume`` can rebuild
        state deterministically.
        """
        if task.status != TaskStatus.SCHEDULED or task not in self._waiting:
            raise ValueError(f"cannot pause task in state {task.status.value}")
        if context is not None:
            task.checkpoint = context.snapshot()
            self._emit(TASK_CHECKPOINTED, task)
        self._waiting.remove(task)
        task.transition(TaskStatus.PAUSED)
        self._emit(TASK_PAUSED, task)
        self.audit.record("paused", task.seq)
        return task

    def checkpoint(self, context: OrchestrationContext) -> None:
        """Executor-facing hook: persist a checkpoint for the running task."""
        task = context.task
        if task.status != TaskStatus.RUNNING:
            raise ValueError("checkpoint is only valid while the task is running")
        task.checkpoint = context.snapshot()
        self._emit(TASK_CHECKPOINTED, task)
        self.audit.record("checkpointed", task.seq)

    def resume(self, task: Task) -> Task:
        """Resume a paused task: it becomes the next task to execute."""
        if task.status != TaskStatus.PAUSED:
            raise ValueError(f"cannot resume task in state {task.status.value}")
        task.transition(TaskStatus.SCHEDULED)
        self._waiting.insert(0, task)
        self._emit(TASK_RESUMED, task)
        self.audit.record("resumed", task.seq)
        return task

    def rollback(self, task: Task) -> Task:
        """Roll back a failed task, if a rollback callable is registered.

        The rollback callable receives the execution context (rebuilt from
        the checkpoint when present) and may report what it reverted.
        """
        if task.status != TaskStatus.FAILED:
            raise ValueError(f"cannot roll back task in state {task.status.value}")
        result: dict[str, Any] | None = None
        if self.rollback_fn is not None:
            result = self.rollback_fn(self._build_context(task))
        task.result = result or {"rolled_back": True}
        task.transition(TaskStatus.ROLLED_BACK)
        self._emit(TASK_ROLLED_BACK, task)
        self.audit.record("rolled_back", task.seq)
        return task

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #
    def get(self, seq: int) -> Task | None:
        return self._tasks.get(seq)

    def tasks(self) -> tuple[Task, ...]:
        return tuple(self._tasks.values())

    def by_status(self, status: TaskStatus) -> tuple[Task, ...]:
        return tuple(t for t in self._tasks.values() if t.status == status)

    def stats(self) -> dict[str, Any]:
        counts = {s.value: 0 for s in TaskStatus}
        for task in self._tasks.values():
            counts[task.status.value] += 1
        return {
            "total": len(self._tasks),
            "running": self.running_count,
            "queued": len(self._queue) + len(self._waiting),
            "waiting_approval": counts[TaskStatus.WAITING_APPROVAL.value],
            "counts": counts,
        }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _find_active(self, key: tuple) -> Task:
        for task in self._tasks.values():
            if task.status in TaskStatus.alive() and task.key() == key:
                return task
        raise ValueError("active task vanished")  # pragma: no cover

    def _release(self, task: Task) -> None:
        self._active_keys.discard(task.key())

    def _emit(self, event_type: str, task: Task, extra: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {
            "task_seq": task.seq,
            "title": task.title,
            "kind": task.kind,
            "status": task.status.value,
        }
        if extra:
            payload.update(extra)
        self.event_bus.publish(event_type, payload)
