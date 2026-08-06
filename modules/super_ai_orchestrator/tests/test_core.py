"""Unit tests: core components (status, task, request, context, events)."""
from __future__ import annotations

from modules.super_ai_orchestrator.core.context import OrchestrationContext
from modules.super_ai_orchestrator.core.request import TaskRequest
from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.core.task import Task
from modules.super_ai_orchestrator.events.bus import EventBus
from modules.super_ai_orchestrator.events.event import Event, TASK_SUBMITTED

from modules.super_ai_orchestrator.tests.helpers import make_task


def test_task_defaults_and_to_dict():
    task = make_task()
    data = task.to_dict()
    assert data["kind"] == "develop"
    assert data["status"] == "pending"
    assert data["priority"] == 5
    assert data["requires"] == []


def test_task_roundtrip_from_dict():
    task = make_task(priority=9, requires=("git", "llm"), status=TaskStatus.QUEUED)
    restored = Task.from_dict(task.to_dict())
    assert restored == task
    assert restored.requires == ("git", "llm")
    assert restored.status == TaskStatus.QUEUED


def test_task_key_is_deterministic():
    a = make_task(payload={"b": 2, "a": 1})
    b = make_task(payload={"a": 1, "b": 2})
    assert a.key() == b.key()
    c = make_task(payload={"a": 1, "b": 3})
    assert a.key() != c.key()


def test_task_transition_valid():
    task = make_task()
    task.transition(TaskStatus.QUEUED)
    task.transition(TaskStatus.SCHEDULED)
    task.transition(TaskStatus.RUNNING)
    task.transition(TaskStatus.COMPLETED)
    assert task.status == TaskStatus.COMPLETED


def test_task_transition_invalid():
    task = make_task()
    with pytest_raises_ValueError():
        task.transition(TaskStatus.COMPLETED)


def test_task_status_terminal_and_alive():
    assert TaskStatus.COMPLETED in TaskStatus.terminal()
    assert TaskStatus.PENDING not in TaskStatus.terminal()
    assert TaskStatus.PENDING in TaskStatus.alive()
    assert TaskStatus.QUEUED in TaskStatus.alive()


def test_task_request_to_task_default_priority():
    request = TaskRequest(kind="repair", title="fix it")
    task = request.to_task(default_priority=7)
    assert task.kind == "repair"
    assert task.priority == 7
    assert task.status == TaskStatus.PENDING

    explicit = TaskRequest(kind="repair", title="fix it", priority=2)
    assert explicit.to_task(default_priority=7).priority == 2


def test_context_snapshot_restore_roundtrip():
    task = make_task()
    context = OrchestrationContext(
        task=task,
        decision={"owner": "developer"},
        plan=({"action": "inspect"},),
        variables={"step": 1},
        checkpoint={"offset": 3},
    )
    snapshot = context.snapshot()
    assert snapshot["variables"] == {"step": 1}

    fresh = OrchestrationContext(task=make_task())
    fresh.restore(snapshot)
    assert fresh.variables == {"step": 1}
    assert fresh.plan == ({"action": "inspect"},)
    assert fresh.decision == {"owner": "developer"}

    payload = fresh.to_dict()
    assert payload["task"]["kind"] == "develop"


def test_event_bus_publishes_in_order():
    bus = EventBus()
    seen: list[tuple[int, str]] = []
    unsubscribe = bus.subscribe(lambda event: seen.append((event.seq, event.type)))

    first = bus.publish(TASK_SUBMITTED, {"a": 1})
    second = bus.publish("task.completed", {"a": 2})
    assert first.seq == 0
    assert second.seq == 1
    assert seen == [(0, TASK_SUBMITTED), (1, "task.completed")]
    assert len(bus.log) == 2
    unsubscribe()

    bus.publish("task.started")
    assert len(seen) == 2  # unsubscribed listener not called


def test_event_bus_history_filter_and_clear():
    bus = EventBus()
    bus.publish(TASK_SUBMITTED)
    bus.publish("task.completed")
    bus.publish(TASK_SUBMITTED)
    assert len(bus.history(TASK_SUBMITTED)) == 2
    assert len(bus.history()) == 3

    bus.clear()
    assert len(bus.log) == 0
    assert bus.seq == 0


def test_event_value_object_to_dict():
    event = Event(type=TASK_SUBMITTED, payload={"seq": 1}, seq=3)
    data = event.to_dict()
    assert data["type"] == TASK_SUBMITTED
    assert data["seq"] == 3
    assert data["payload"] == {"seq": 1}


# -- local helper so the core suite stays stdlib-only -------------------- #
def pytest_raises_ValueError():
    from contextlib import contextmanager

    @contextmanager
    def _cm():
        try:
            yield
        except ValueError:
            return
        raise AssertionError("expected ValueError")

    return _cm()
