"""Fluent builder for workflow definitions."""

from __future__ import annotations

from typing import Any

from automation.automation_models import WorkflowDefinition, WorkflowStep


class WorkflowBuilder:
    """Builds WorkflowDefinition instances with a fluent API."""

    def __init__(self) -> None:
        self._workflow_id = ""
        self._name = ""
        self._description = ""
        self._steps: list[WorkflowStep] = []
        self._triggers: list[str] = []
        self._tags: list[str] = []
        self._active = True
        self._version = "1.0.0"

    def id(self, workflow_id: str) -> "WorkflowBuilder":
        self._workflow_id = workflow_id
        return self

    def name(self, name: str) -> "WorkflowBuilder":
        self._name = name
        return self

    def description(self, description: str) -> "WorkflowBuilder":
        self._description = description
        return self

    def step(self, step_id: str, action: str,
             params: dict[str, Any] | None = None,
             next_on_success: str | None = None,
             next_on_failure: str | None = None,
             timeout: float | None = None) -> "WorkflowBuilder":
        self._steps.append(WorkflowStep(
            step_id=step_id, action=action, params=params or {},
            next_on_success=next_on_success,
            next_on_failure=next_on_failure, timeout=timeout))
        return self

    def trigger(self, trigger_id: str) -> "WorkflowBuilder":
        self._triggers.append(trigger_id)
        return self

    def tag(self, tag: str) -> "WorkflowBuilder":
        self._tags.append(tag)
        return self

    def active(self, active: bool) -> "WorkflowBuilder":
        self._active = active
        return self

    def version(self, version: str) -> "WorkflowBuilder":
        self._version = version
        return self

    def build(self) -> WorkflowDefinition:
        return WorkflowDefinition(
            workflow_id=self._workflow_id,
            name=self._name,
            description=self._description,
            steps=list(self._steps),
            triggers=list(self._triggers),
            active=self._active,
            version=self._version,
            tags=list(self._tags),
        )
