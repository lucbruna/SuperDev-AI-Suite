from __future__ import annotations

from typing import Any


class WorkflowDefinition:
    """A stored workflow definition."""

    def __init__(self, workflow_id: str, name: str, steps: list[dict[str, Any]], description: str = ""):
        self._workflow_id = workflow_id
        self._name = name
        self._steps = list(steps)
        self._description = description

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def steps(self) -> list[dict[str, Any]]:
        return list(self._steps)

    @property
    def description(self) -> str:
        return self._description

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self._workflow_id,
            "name": self._name,
            "steps": list(self._steps),
            "description": self._description,
        }


class WorkflowRepository:
    """Storage for reusable workflow definitions."""

    def __init__(self):
        self._workflows: dict[str, WorkflowDefinition] = {}

    @property
    def count(self) -> int:
        return len(self._workflows)

    def add(self, workflow: WorkflowDefinition) -> None:
        self._workflows[workflow.workflow_id] = workflow

    def get(self, workflow_id: str) -> WorkflowDefinition | None:
        return self._workflows.get(workflow_id)

    def remove(self, workflow_id: str) -> bool:
        return self._workflows.pop(workflow_id, None) is not None

    def search(self, query: str) -> list[WorkflowDefinition]:
        q = query.lower()
        return [w for w in self._workflows.values() if q in w.name.lower() or q in w.description.lower()]

    def list_all(self) -> list[WorkflowDefinition]:
        return list(self._workflows.values())

    def clear(self) -> None:
        self._workflows.clear()
