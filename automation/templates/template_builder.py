"""Fluent builder for workflow templates."""

from __future__ import annotations

from typing import Any

from automation.templates.template_models import (
    TemplateParameter,
    WorkflowTemplate,
)


class TemplateBuilder:
    """Builds a WorkflowTemplate step by step."""

    def __init__(self) -> None:
        self._template = WorkflowTemplate(template_id="", name="")

    def id(self, template_id: str) -> "TemplateBuilder":
        self._template.template_id = template_id
        return self

    def name(self, name: str) -> "TemplateBuilder":
        self._template.name = name
        return self

    def description(self, description: str) -> "TemplateBuilder":
        self._template.description = description
        return self

    def category(self, category: str) -> "TemplateBuilder":
        self._template.category = category
        return self

    def step(self, stage_id: str, action: str,
             params: dict[str, Any] | None = None,
             next_on_success: str | None = None,
             next_on_failure: str | None = None,
             timeout: float | None = None) -> "TemplateBuilder":
        step: dict[str, Any] = {
            "stage_id": stage_id,
            "action": action,
            "params": params or {},
        }
        if next_on_success is not None:
            step["next_on_success"] = next_on_success
        if next_on_failure is not None:
            step["next_on_failure"] = next_on_failure
        if timeout is not None:
            step["timeout"] = timeout
        self._template.steps.append(step)
        return self

    def parameter(self, name: str, required: bool = False,
                  default: Any = None,
                  description: str = "") -> "TemplateBuilder":
        self._template.parameters.append(TemplateParameter(
            name=name, required=required, default=default,
            description=description))
        return self

    def build(self) -> WorkflowTemplate:
        return self._template
