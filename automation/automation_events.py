"""Event bus for automation engine lifecycle events."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable


class AutomationEventType(Enum):
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    SCHEDULE_FIRED = "schedule.fired"
    TRIGGER_FIRED = "trigger.fired"
    AUTOMATION_SUGGESTED = "automation.suggested"


class AutomationEvents:
    """Lightweight in-process pub/sub."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.automation.events")
        self._listeners: dict[AutomationEventType, list[Callable[[dict[str, Any]], None]]] = {}

    def on(self, event_type: AutomationEventType,
           listener: Callable[[dict[str, Any]], None]) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def off(self, event_type: AutomationEventType,
            listener: Callable[[dict[str, Any]], None]) -> None:
        listeners = self._listeners.get(event_type, [])
        if listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type: AutomationEventType,
                data: dict[str, Any] | None = None) -> None:
        payload = {"type": event_type.value, **(data or {})}
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(payload)
            except Exception as exc:  # noqa: BLE001
                self._log.warning(
                    "listener failed for %s: %s", event_type.value, exc)

    def once(self, event_type: AutomationEventType,
             listener: Callable[[dict[str, Any]], None]) -> None:
        def wrapper(data: dict[str, Any]) -> None:
            self.off(event_type, wrapper)
            listener(data)

        self.on(event_type, wrapper)

    def listener_count(self, event_type: AutomationEventType) -> int:
        return len(self._listeners.get(event_type, []))
