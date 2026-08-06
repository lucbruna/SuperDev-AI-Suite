"""Unit tests: kernel (queue, audit, lifecycle, control, dedupe, capacity)."""
from __future__ import annotations

from modules.super_ai_orchestrator.config import KernelConfig
from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.events.event import (
    KERNEL_DEDUPED,
    TASK_CANCELLED,
    TASK_COMPLETED,
    TASK_PAUSED,
    TASK_SCHEDULED,
    TASK_STARTED,
    TASK_SUBMITTED,
    TASK_WAITING_APPROVAL,
)
from modules.super_ai_orchestrator.kernel import OrchestrationKernel
from modules.super_ai_orchestrator.kernel.audit import AuditTrail
from modules.super_ai_orchestrator.kernel.kernel import QueueFullError
from modules.super_ai_orchestrator.kernel.queue import PriorityQueue

from modules.super_ai_orchestrator.tests.helpers import make_task


def _kernel(governance: bool = False, **overrides) -> OrchestrationKernel:
    return OrchestrationKernel(KernelConfig(governance_required=governance, **overrides))


# ---------------------------------------------------------------------- #
# PriorityQueue
# ---------------------------------------------------------------------- #
def test_priority_queue_orders_by_priority_then_seq():
    queue = PriorityQueue()
    low = make_task(title="low", priority=2, seq=0)
    high = make_task(title="high", priority=9, seq=1)
    mid = make_task(title="mid", priority=5, seq=2)
    for task in (low, high, mid):
        queue.push(task)

    assert queue.peek() is high
    assert queue.pop() is high
    assert queue.pop() is mid
    assert queue.pop() is low
    assert queue.pop() is None


def test_priority_queue_tie_breaks_by_seq():
    queue = PriorityQueue()
    a = make_task(title="a", priority=5, seq=0)
    b = make_task(title="b", priority=5, seq=1)
    queue.push(b)
    queue.push(a)
    assert queue.pop() is a
    assert queue.pop() is b


def test_priority_queue_remove_and_contains():
    queue = PriorityQueue()
    task = make_task(seq=7)
    queue.push(task)
    assert queue.contains(7)
    assert queue.remove(7) is task
    assert not queue.contains(7)
    assert queue.remove(7) is None
    assert len(queue) == 0


# ---------------------------------------------------------------------- #
# AuditTrail
# ---------------------------------------------------------------------- #
def test_audit_trail_append_only_and_ordered():
    trail = AuditTrail()
    first = trail.record("submit", task_seq=1)
    second = trail.record("complete", task_seq=1, detail={"ok": True})
    assert first.seq == 0
    assert second.seq == 1
    assert [r.kind for r in trail.all()] == ["submit", "complete"]
    assert len(trail.for_task(1)) == 2
    assert trail.for_task(99) == ()
    assert trail.kinds() == ("submit", "complete")


# ---------------------------------------------------------------------- #
# Kernel: submission & governance
# ---------------------------------------------------------------------- #
def test_kernel_submit_assigns_monotonic_seq_and_events():
    kernel = _kernel(governance=False)
    seen: list[str] = []
    kernel.event_bus.subscribe(lambda event: seen.append(event.type))

    first = kernel.submit(make_task())
    second = kernel.submit(make_task(title="other"))
    assert first.seq == 0
    assert second.seq == 1
    assert first.status == TaskStatus.QUEUED
    assert TASK_SUBMITTED in seen
    assert TASK_SUBMITTED in [e.type for e in kernel.event_bus.log]


def test_kernel_submit_requires_pending():
    kernel = _kernel(governance=False)
    task = make_task(status=TaskStatus.QUEUED)
    try:
        kernel.submit(task)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_kernel_submit_validates_priority_range():
    kernel = _kernel(governance=False)
    for bad in (0, 11):
        try:
            kernel.submit(make_task(priority=bad))
            raise AssertionError("expected ValueError")
        except ValueError:
            pass


def test_kernel_gates_task_when_governance_enabled():
    kernel = _kernel(governance=True)
    task = kernel.submit(make_task())
    assert task.status == TaskStatus.WAITING_APPROVAL
    assert kernel.stats()["waiting_approval"] == 1

    approved = kernel.approve(task)
    assert approved.status == TaskStatus.QUEUED

    other = kernel.submit(make_task(title="rejected one"))
    rejected = kernel.reject(other, reason="nope")
    assert rejected.status == TaskStatus.REJECTED
    assert rejected.reason == "nope"


def test_kernel_deduplicates_identical_active_tasks():
    kernel = _kernel(governance=False)
    first = kernel.submit(make_task(title="same"))
    duplicate = kernel.submit(make_task(title="same"))
    assert duplicate is first
    assert kernel.stats()["total"] == 1
    assert KERNEL_DEDUPED in [e.type for e in kernel.event_bus.log]
    assert "deduped" in kernel.audit.kinds()


def test_kernel_queue_full_raises():
    kernel = _kernel(governance=False, queue_capacity=1)
    kernel.submit(make_task(title="one"))
    try:
        kernel.submit(make_task(title="two"))
        raise AssertionError("expected QueueFullError")
    except QueueFullError:
        pass


# ---------------------------------------------------------------------- #
# Kernel: scheduling & execution
# ---------------------------------------------------------------------- #
def test_kernel_tick_schedules_in_priority_order():
    kernel = _kernel(governance=False)
    kernel.submit(make_task(title="low", priority=2))
    kernel.submit(make_task(title="high", priority=9))
    kernel.submit(make_task(title="mid", priority=5))

    order: list[str] = []
    kernel.set_executor(lambda ctx: order.append(ctx.task.title) or {"status": "ok"})

    processed = kernel.tick(slices=3)
    assert processed == 3
    assert order == ["high", "mid", "low"]
    assert kernel.stats()["counts"]["completed"] == 3
    assert TASK_SCHEDULED in [e.type for e in kernel.event_bus.log]


def test_kernel_executes_task_to_completion():
    kernel = _kernel(governance=False)

    def executor(context):
        return {"status": "ok", "kind": context.task.kind}

    kernel.set_executor(executor)
    task = kernel.submit(make_task())
    assert kernel.tick() >= 1

    assert task.status == TaskStatus.COMPLETED
    assert task.result == {"status": "ok", "kind": "develop"}
    assert "started" in kernel.audit.kinds()
    assert "completed" in kernel.audit.kinds()
    assert TASK_STARTED in [e.type for e in kernel.event_bus.log]
    assert TASK_COMPLETED in [e.type for e in kernel.event_bus.log]
    assert kernel.stats()["counts"]["completed"] == 1


def test_kernel_records_failure_and_rolls_back_when_configured():
    kernel = _kernel(governance=False, rollback_on_failure=True)
    kernel.set_executor(lambda context: 1 / 0)  # deterministic failure
    kernel.set_rollback(lambda context: {"rolled_back": True})

    task = kernel.submit(make_task())
    kernel.tick()
    assert task.status == TaskStatus.ROLLED_BACK
    assert task.result == {"rolled_back": True}
    assert "failed" in kernel.audit.kinds()
    assert "rolled_back" in kernel.audit.kinds()


def test_kernel_cancel_queued_task():
    kernel = _kernel(governance=False)
    task = kernel.submit(make_task())
    kernel.cancel(task)
    assert task.status == TaskStatus.CANCELLED
    assert task.reason == "cancelled"
    assert TASK_CANCELLED in [e.type for e in kernel.event_bus.log]


def test_kernel_cannot_cancel_terminal_or_running():
    kernel = _kernel(governance=False)
    done = kernel.submit(make_task())
    kernel.cancel(done)
    try:
        kernel.cancel(done)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    running = make_task()
    running.status = TaskStatus.RUNNING
    try:
        kernel.cancel(running)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_kernel_pause_resume_checkpoint_cycle():
    kernel = _kernel(governance=False)
    task = kernel.submit(make_task())
    kernel.tick(slices=1)  # SCHEDULED, parked in _waiting (no executor)
    assert task.status == TaskStatus.SCHEDULED

    kernel.pause(task)
    assert task.status == TaskStatus.PAUSED
    assert TASK_PAUSED in [e.type for e in kernel.event_bus.log]

    kernel.resume(task)
    assert task.status == TaskStatus.SCHEDULED

    kernel.cancel(task)
    assert task.status == TaskStatus.CANCELLED


def test_kernel_checkpoint_hook_during_execution():
    kernel = _kernel(governance=False)
    captured: dict = {}

    def executor(context):
        context.variables["step"] = 1
        kernel.checkpoint(context)
        captured["checkpoint"] = context.task.checkpoint
        return {"status": "ok"}

    kernel.set_executor(executor)
    task = kernel.submit(make_task())
    kernel.tick()
    assert task.status == TaskStatus.COMPLETED
    assert captured["checkpoint"]["variables"] == {"step": 1}


def test_kernel_planner_attaches_plan_to_context():
    kernel = _kernel(governance=False)
    kernel.set_planner(lambda task: [{"action": "inspect"}, {"action": "verify"}])
    seen: list[list[dict]] = []

    def executor(context):
        seen.append(list(context.plan))
        return {"status": "ok"}

    kernel.set_executor(executor)
    task = kernel.submit(make_task())
    kernel.tick()
    assert task.status == TaskStatus.COMPLETED
    assert seen[0] == [{"action": "inspect"}, {"action": "verify"}]
