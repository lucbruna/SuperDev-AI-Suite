"""Manager for workflows, triggers, schedules, and executions."""

from __future__ import annotations

import time
from typing import Any, Callable

from .automation_context import AutomationContext
from .automation_events import AutomationEventType, AutomationEvents
from .automation_logger import get_logger
from .automation_metrics import AutomationMetrics
from .automation_models import (AutomationResult, ExecutionRecord, ScheduleSpec,
                               TriggerSpec, WorkflowDefinition, WorkflowStatus)
from .automation_registry import AutomationRegistry
from .automation_security import AutomationSecurity


class AutomationManager:
    """CRUD for workflows plus execution dispatch."""

    def __init__(self, registry: AutomationRegistry,
                 security: AutomationSecurity,
                 events: AutomationEvents,
                 metrics: AutomationMetrics) -> None:
        self._log = get_logger("manager")
        self.registry = registry
        self.security = security
        self.events = events
        self.metrics = metrics
        self._executions: dict[str, ExecutionRecord] = {}
        self._handlers: dict[str, Callable[[str, dict[str, Any]], Any]] = {}
        self._triggers: dict[str, Callable[[dict[str, Any]], bool]] = {}

    # -- workflows ---------------------------------------------------------
    def create_workflow(self, workflow: WorkflowDefinition) -> None:
        self.registry.register_workflow(workflow)
        self.events.publish(AutomationEventType.WORKFLOW_CREATED,
                            {"workflow_id": workflow.workflow_id})

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        return self.registry.get_workflow(workflow_id)

    def remove_workflow(self, workflow_id: str) -> bool:
        return self.registry.remove_workflow(workflow_id)

    def list_workflows(self) -> list[str]:
        return self.registry.list_workflows()

    # -- action handlers ---------------------------------------------------
    def register_action(self, action: str,
                        handler: Callable[[dict[str, Any]], Any]) -> None:
        self.registry.register_action(action, handler)

    def has_action(self, action: str) -> bool:
        return self.registry.has_action(action)

    # -- triggers ----------------------------------------------------------
    def register_trigger(self, trigger: TriggerSpec,
                         evaluator: Callable[[dict[str, Any]], bool]) -> None:
        self.registry.register_trigger(trigger.trigger_id,
                                       trigger.trigger_type.value,
                                       trigger.config)
        self._triggers[trigger.trigger_id] = evaluator

    def fire_trigger(self, trigger_id: str, event: dict[str, Any]) -> bool:
        evaluator = self._triggers.get(trigger_id)
        if evaluator is None:
            return False
        fired = evaluator(event)
        if fired:
            self.events.publish(AutomationEventType.TRIGGER_FIRED,
                                {"trigger_id": trigger_id})
        return fired

    # -- schedules ---------------------------------------------------------
    def register_schedule(self, schedule: ScheduleSpec) -> None:
        self.registry.register_schedule(schedule)

    # -- execution ---------------------------------------------------------
    def execute(self, workflow_id: str,
                payload: dict[str, Any] | None = None) -> AutomationResult:
        workflow = self.registry.get_workflow(workflow_id)
        if workflow is None:
            return AutomationResult(False, error=f"workflow not found: {workflow_id}")
        if not workflow.active:
            return AutomationResult(False, error=f"workflow inactive: {workflow_id}")
        if not workflow.steps:
            return AutomationResult(False, error=f"workflow has no steps: {workflow_id}")

        record = ExecutionRecord(
            execution_id=f"exec-{int(time.time() * 1000)}",
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=time.time(),
        )
        self._executions[record.execution_id] = record
        self.metrics.increment("executions.started")
        self.events.publish(AutomationEventType.WORKFLOW_STARTED,
                            {"execution_id": record.execution_id})

        context = AutomationContext(workflow_id, payload)
        steps = {s.step_id: s for s in workflow.steps}
        order = [s.step_id for s in workflow.steps]

        try:
            for step_id in order:
                step = steps[step_id]
                action = step.action
                if not self.security.can_execute(action):
                    raise PermissionError(f"action not allowed: {action}")
                handler = self.registry.get_action(action)
                if handler is None:
                    raise ValueError(f"no handler for action: {action}")
                self.events.publish(AutomationEventType.TASK_STARTED,
                                    {"step_id": step_id, "action": action})
                result = handler(dict(step.params, **context.attributes))
                context.record_step(step_id, result)
                context.attributes.update(result if isinstance(result, dict) else {})
                record.steps_completed += 1
                self.metrics.increment("tasks.completed")
                self.events.publish(AutomationEventType.TASK_COMPLETED,
                                    {"step_id": step_id})
        except Exception as exc:  # noqa: BLE001
            record.status = WorkflowStatus.FAILED
            record.error = str(exc)
            record.finished_at = time.time()
            self.metrics.increment("executions.failed")
            self.events.publish(AutomationEventType.WORKFLOW_FAILED,
                                {"execution_id": record.execution_id,
                                 "error": str(exc)})
            return AutomationResult(False, error=str(exc),
                                    result={"execution_id": record.execution_id})

        record.status = WorkflowStatus.COMPLETED
        record.finished_at = time.time()
        record.result = context.attributes
        self.metrics.increment("executions.completed")
        self.events.publish(AutomationEventType.WORKFLOW_COMPLETED,
                            {"execution_id": record.execution_id})
        return AutomationResult(True, result={
            "execution_id": record.execution_id,
            "attributes": context.attributes,
        })

    def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        return self._executions.get(execution_id)

    def list_executions(self, limit: int = 50) -> list[dict[str, Any]]:
        return [r.to_dict() for r in list(self._executions.values())[-limit:]]

    def snapshot(self) -> dict[str, int]:
        return self.registry.snapshot()
