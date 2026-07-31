"""Registry for workflows, triggers, and action handlers."""

from __future__ import annotations

import logging
from typing import Any, Callable


class AutomationRegistry:
    """Registers workflows, triggers, schedules, and action handlers."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.automation.registry")
        self._workflows: dict[str, Any] = {}
        self._triggers: dict[str, dict[str, Any]] = {}
        self._schedules: dict[str, dict[str, Any]] = {}
        self._actions: dict[str, Callable[[dict[str, Any]], Any]] = {}

    # -- workflows ---------------------------------------------------------
    def register_workflow(self, workflow: Any) -> None:
        self._workflows[workflow.workflow_id] = workflow

    def get_workflow(self, workflow_id: str) -> Any | None:
        return self._workflows.get(workflow_id)

    def remove_workflow(self, workflow_id: str) -> bool:
        return self._workflows.pop(workflow_id, None) is not None

    def list_workflows(self) -> list[str]:
        return list(self._workflows)

    # -- triggers ----------------------------------------------------------
    def register_trigger(self, trigger_id: str, trigger_type: str,
                         config: dict[str, Any]) -> None:
        self._triggers[trigger_id] = {"type": trigger_type, "config": config}

    def get_trigger(self, trigger_id: str) -> dict[str, Any] | None:
        return self._triggers.get(trigger_id)

    def list_triggers(self) -> list[str]:
        return list(self._triggers)

    # -- schedules ---------------------------------------------------------
    def register_schedule(self, schedule: Any) -> None:
        self._schedules[schedule.schedule_id] = schedule

    def get_schedule(self, schedule_id: str) -> Any | None:
        return self._schedules.get(schedule_id)

    def list_schedules(self) -> list[str]:
        return list(self._schedules)

    # -- action handlers ---------------------------------------------------
    def register_action(self, action: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        self._actions[action] = handler

    def get_action(self, action: str) -> Callable[[dict[str, Any]], Any] | None:
        return self._actions.get(action)

    def has_action(self, action: str) -> bool:
        return action in self._actions

    def list_actions(self) -> list[str]:
        return list(self._actions)

    def snapshot(self) -> dict[str, int]:
        return {
            "workflows": len(self._workflows),
            "triggers": len(self._triggers),
            "schedules": len(self._schedules),
            "actions": len(self._actions),
        }
