"""Workflow store: registration, validation, versioning, and history."""

from __future__ import annotations

from typing import Any

from automation.workflow.workflow_executor import WorkflowExecutor
from automation.workflow.workflow_state import WorkflowState
from automation.workflow.workflow_validator import WorkflowValidator
from automation.workflow.workflow_version import WorkflowVersioner


class WorkflowManager:
    """Registers workflows, runs them, and keeps run history."""

    def __init__(self, validator: WorkflowValidator | None = None,
                 versioner: WorkflowVersioner | None = None,
                 executor: WorkflowExecutor | None = None) -> None:
        self.validator = validator or WorkflowValidator()
        self.versioner = versioner or WorkflowVersioner()
        self.executor = executor or WorkflowExecutor()
        self._workflows: dict[str, Any] = {}
        self._history: list[WorkflowState] = []

    def register(self, definition: Any) -> list[str] | None:
        """Validates and registers a workflow. Returns issues or None."""
        issues = self.validator.validate(definition)
        if issues:
            return issues
        self._workflows[definition.workflow_id] = definition
        self.versioner.register(definition)
        return None

    def get(self, workflow_id: str) -> Any | None:
        return self._workflows.get(workflow_id)

    def list(self) -> list[str]:
        return list(self._workflows)

    def remove(self, workflow_id: str) -> bool:
        return self._workflows.pop(workflow_id, None) is not None

    def register_action(self, action: str, handler: Any) -> None:
        self.executor.register_action(action, handler)

    def run(self, workflow_id: str,
            initial_vars: dict[str, Any] | None = None) -> WorkflowState | None:
        definition = self._workflows.get(workflow_id)
        if definition is None:
            return None
        state = self.executor.run(definition, initial_vars)
        self._history.append(state)
        return state

    def history(self, limit: int = 50) -> list[WorkflowState]:
        return list(self._history[-limit:])
