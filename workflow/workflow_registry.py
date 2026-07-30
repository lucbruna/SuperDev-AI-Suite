from __future__ import annotations

import logging
from typing import Any

from .workflow_models import WorkflowDefinition


class WorkflowRegistry:
    """Registry for workflow definitions."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._log = logging.getLogger("superdev.workflow.registry")

    def register(self, workflow_id: str, definition: WorkflowDefinition) -> None:
        self._workflows[workflow_id] = definition

    def get(self, workflow_id: str) -> WorkflowDefinition | None:
        return self._workflows.get(workflow_id)

    def unregister(self, workflow_id: str) -> bool:
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            return True
        return False

    def list_all(self) -> list[WorkflowDefinition]:
        return list(self._workflows.values())

    def list_by_status(self, status: str) -> list[WorkflowDefinition]:
        return [w for w in self._workflows.values() if w.status.value == status]

    def count(self) -> int:
        return len(self._workflows)

    def clear(self) -> None:
        self._workflows.clear()
