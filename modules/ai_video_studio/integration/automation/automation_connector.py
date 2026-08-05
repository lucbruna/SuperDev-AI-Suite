"""Automation Connector — facade over workflow, triggers, scheduler and events."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.automation.event_listener import (
    get_event_listener,
)
from modules.ai_video_studio.integration.automation.scheduler_bridge import (
    get_scheduler_bridge,
)
from modules.ai_video_studio.integration.automation.trigger_manager import (
    get_trigger_manager,
)
from modules.ai_video_studio.integration.automation.workflow_builder import (
    get_workflow_builder,
)
from modules.ai_video_studio.integration.connector_base import DomainConnector


class AutomationConnector(DomainConnector):
    """Builds workflows, manages triggers and bridges scheduling and events."""

    domain = "automation"
    description = "Workflow building, triggers, scheduling and event listeners"

    def __init__(self) -> None:
        super().__init__()
        self._register("build_workflow", self._workflow)
        self._register("register_trigger", self._trigger)
        self._register("next_run", self._next_run)
        self._register("listeners", lambda d: get_event_listener().list())

    def _workflow(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_workflow_builder().build(data.get("name", "workflow"),
                                            steps=data.get("steps"))

    def _trigger(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_trigger_manager().register(data.get("name", "trigger"),
                                              event=data.get("event", "video.ready"))

    def _next_run(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_scheduler_bridge().next_run(data.get("cron", "0 6 * * *"))


_automation_connector: AutomationConnector | None = None


def get_automation_connector() -> AutomationConnector:
    global _automation_connector
    if _automation_connector is None:
        _automation_connector = AutomationConnector()
    return _automation_connector
