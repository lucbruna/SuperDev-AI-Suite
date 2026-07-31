"""Events for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from agent_orchestration.orchestrator_logger import get_logger

_Listener = Callable[[dict[str, Any]], None]


class OrchestratorEventType(Enum):
    AGENT_REGISTERED = "ao.agent.registered"
    AGENT_UPDATED = "ao.agent.updated"
    AGENT_REMOVED = "ao.agent.removed"
    AGENT_STATUS_CHANGED = "ao.agent.status"
    TASK_PLANNED = "ao.task.planned"
    TASK_QUEUED = "ao.task.queued"
    TASK_STARTED = "ao.task.started"
    TASK_COMPLETED = "ao.task.completed"
    TASK_FAILED = "ao.task.failed"
    TASK_CANCELLED = "ao.task.cancelled"
    MESSAGE_SENT = "ao.message.sent"
    APPROVAL_REQUIRED = "ao.approval.required"
    APPROVAL_RESOLVED = "ao.approval.resolved"
    DECISION_MADE = "ao.decision.made"
    LESSON_LEARNED = "ao.lesson.learned"


class OrchestratorEvents:
    """Thread-safe pub/sub event bus with listener isolation."""

    def __init__(self) -> None:
        self._log = get_logger("events")
        self._listeners: dict[OrchestratorEventType, list[_Listener]] = {}

    def on(self, event_type: OrchestratorEventType,
           listener: _Listener) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def once(self, event_type: OrchestratorEventType,
             listener: _Listener) -> None:
        def _wrapper(payload: dict[str, Any]) -> None:
            self.off(event_type, _wrapper)
            listener(payload)

        self.on(event_type, _wrapper)

    def off(self, event_type: OrchestratorEventType,
            listener: _Listener) -> None:
        listeners = self._listeners.get(event_type)
        if listeners is not None and listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type: OrchestratorEventType,
                payload: dict[str, Any]) -> None:
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(payload)
            except Exception:  # noqa: BLE001 - listener isolation
                self._log.warning("listener failed for %s: %s",
                                  event_type.value, listener)
