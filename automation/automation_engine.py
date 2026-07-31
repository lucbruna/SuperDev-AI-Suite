"""Automation engine: facade for the Autonomous Workflow & Automation subsystem."""

from __future__ import annotations

import logging
from typing import Any, Callable

from .automation_config import AutomationConfig
from .automation_events import AutomationEvents
from .automation_manager import AutomationManager
from .automation_metrics import AutomationMetrics
from .automation_models import (AutomationResult, ScheduleSpec, TriggerSpec,
                               WorkflowDefinition)
from .automation_registry import AutomationRegistry
from .automation_runtime import AutomationRuntime
from .automation_security import AutomationSecurity


class AutomationEngine:
    """Facade over manager, runtime, registry, events, metrics, and security."""

    def __init__(self, config: AutomationConfig,
                 manager: AutomationManager,
                 runtime: AutomationRuntime,
                 registry: AutomationRegistry,
                 events: AutomationEvents,
                 metrics: AutomationMetrics,
                 security: AutomationSecurity) -> None:
        self._log = logging.getLogger("superdev.automation")
        self.config = config
        self.manager = manager
        self.runtime = runtime
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.security = security

    # -- lifecycle ---------------------------------------------------------
    def initialize(self) -> None:
        self.runtime.start()

    def shutdown(self) -> None:
        self.runtime.stop()

    def is_running(self) -> bool:
        return self.runtime.running

    # -- workflows ---------------------------------------------------------
    def create_workflow(self, workflow: WorkflowDefinition) -> None:
        self.manager.create_workflow(workflow)

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        return self.manager.get_workflow(workflow_id)

    def remove_workflow(self, workflow_id: str) -> bool:
        return self.manager.remove_workflow(workflow_id)

    def list_workflows(self) -> list[str]:
        return self.manager.list_workflows()

    # -- actions -----------------------------------------------------------
    def register_action(self, action: str,
                        handler: Callable[[dict[str, Any]], Any]) -> None:
        self.manager.register_action(action, handler)

    def has_action(self, action: str) -> bool:
        return self.manager.has_action(action)

    # -- triggers and schedules --------------------------------------------
    def register_trigger(self, trigger: TriggerSpec,
                         evaluator: Callable[[dict[str, Any]], bool]) -> None:
        self.manager.register_trigger(trigger, evaluator)

    def fire_trigger(self, trigger_id: str, event: dict[str, Any]) -> bool:
        return self.manager.fire_trigger(trigger_id, event)

    def register_schedule(self, schedule: ScheduleSpec) -> None:
        self.manager.register_schedule(schedule)

    # -- execution ---------------------------------------------------------
    def execute(self, workflow_id: str,
                payload: dict[str, Any] | None = None) -> AutomationResult:
        return self.manager.execute(workflow_id, payload)

    def run(self, workflow_id: str,
            payload: dict[str, Any] | None = None) -> AutomationResult:
        return self.execute(workflow_id, payload)

    def get_execution(self, execution_id: str) -> Any:
        return self.manager.get_execution(execution_id)

    # -- observation -------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "registry": self.registry.snapshot(),
            "metrics": self.metrics.snapshot(),
            "executions": len(self.manager.list_executions()),
        }
