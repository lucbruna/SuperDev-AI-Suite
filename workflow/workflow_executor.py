from __future__ import annotations

import logging
import time
from typing import Any, Callable

from .workflow_models import WorkflowStep, StepStatus
from .workflow_interfaces import IWorkflowExecutor


class WorkflowExecutor(IWorkflowExecutor):
    """Executes individual workflow steps."""

    def __init__(self) -> None:
        self._actions: dict[str, Callable[..., Any]] = {}
        self._log = logging.getLogger("superdev.workflow.executor")

    def register_action(self, name: str, action: Callable[..., Any]) -> None:
        self._actions[name] = action

    def execute_step(self, step_id: str, context: dict[str, Any]) -> Any:
        step = context.get("step")
        if not step or not isinstance(step, WorkflowStep):
            raise ValueError("Step not found in context")

        action = self._actions.get(step.action)
        if not action:
            raise ValueError(f"No action registered for: {step.action}")

        step.status = StepStatus.RUNNING
        try:
            result = action(**context.get("params", {}))
            step.status = StepStatus.COMPLETED
            step.result = {"output": result}
            return result
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            raise

    def can_execute(self, step_id: str) -> bool:
        return step_id in self._actions
