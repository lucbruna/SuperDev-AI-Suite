"""Workflow engine: facade for the workflow subsystem."""

from __future__ import annotations

from typing import Any, Callable

from automation.workflow.workflow_builder import WorkflowBuilder
from automation.workflow.workflow_manager import WorkflowManager
from automation.workflow.workflow_state import WorkflowState
from automation.workflow.workflow_validator import WorkflowValidator


class WorkflowEngine:
    """Builds, registers, and runs workflows."""

    def __init__(self, manager: WorkflowManager | None = None) -> None:
        self.manager = manager or WorkflowManager()
        self.executor = self.manager.executor
        self.versioner = self.manager.versioner
        self.validator: WorkflowValidator = self.manager.validator

    # -- building ----------------------------------------------------------
    def build(self) -> WorkflowBuilder:
        return WorkflowBuilder()

    # -- registration ------------------------------------------------------
    def register(self, definition: Any) -> list[str] | None:
        return self.manager.register(definition)

    def get(self, workflow_id: str) -> Any | None:
        return self.manager.get(workflow_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, workflow_id: str) -> bool:
        return self.manager.remove(workflow_id)

    def validate(self, definition: Any) -> list[str]:
        return self.validator.validate(definition)

    # -- actions -----------------------------------------------------------
    def register_action(self, action: str,
                        handler: Callable[[dict[str, Any]], Any]) -> None:
        self.manager.register_action(action, handler)

    # -- execution ---------------------------------------------------------
    def run(self, workflow_id: str,
            initial_vars: dict[str, Any] | None = None) -> WorkflowState | None:
        return self.manager.run(workflow_id, initial_vars)

    def history(self, limit: int = 50) -> list[WorkflowState]:
        return self.manager.history(limit)

    # -- versioning --------------------------------------------------------
    def version_of(self, workflow_id: str) -> str | None:
        return self.versioner.version_of(workflow_id)

    def versions(self, workflow_id: str) -> list[Any]:
        return self.versioner.history(workflow_id)
