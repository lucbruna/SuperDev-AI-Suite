"""Template engine: facade for the templates subsystem."""

from __future__ import annotations

from typing import Any

from automation.automation_models import WorkflowDefinition, WorkflowStep
from automation.templates.template_builder import TemplateBuilder
from automation.templates.template_history import TemplateHistory
from automation.templates.template_models import WorkflowTemplate
from automation.templates.template_renderer import TemplateRenderer
from automation.templates.template_validator import TemplateValidator


class TemplateEngine:
    """Registers templates and instantiates them into workflows."""

    def __init__(self, validator: TemplateValidator | None = None,
                 renderer: TemplateRenderer | None = None,
                 history: TemplateHistory | None = None) -> None:
        self.validator = validator or TemplateValidator()
        self.renderer = renderer or TemplateRenderer()
        self.history = history or TemplateHistory()
        self._templates: dict[str, WorkflowTemplate] = {}

    def build(self) -> TemplateBuilder:
        return TemplateBuilder()

    def register(self, template: WorkflowTemplate) -> list[str] | None:
        issues = self.validator.validate(template)
        if issues:
            return issues
        self._templates[template.template_id] = template
        return None

    def get(self, template_id: str) -> WorkflowTemplate | None:
        return self._templates.get(template_id)

    def list(self) -> list[str]:
        return list(self._templates)

    def remove(self, template_id: str) -> bool:
        return self._templates.pop(template_id, None) is not None

    def instantiate(self, template_id: str,
                    variables: dict[str, Any]) -> WorkflowDefinition | None:
        """Creates a WorkflowDefinition, filling defaults for optional params."""
        template = self._templates.get(template_id)
        if template is None:
            return None
        values = dict(variables)
        for param in template.parameters:
            if param.name not in values and param.default is not None:
                values[param.name] = param.default
        missing = [p.name for p in template.parameters
                   if p.required and p.name not in values]
        if missing:
            self.history.record(template_id, variables, ok=False,
                                error=f"missing required parameters: "
                                      f"{', '.join(missing)}")
            raise ValueError(f"missing required parameters: "
                             f"{', '.join(missing)}")
        steps = self.renderer.render(template.steps, values)
        definition = WorkflowDefinition(
            workflow_id=template_id,
            name=template.name,
            description=template.description,
            steps=[WorkflowStep(
                step_id=step.get("stage_id", ""),
                action=step.get("action", ""),
                params=step.get("params", {}),
                next_on_success=step.get("next_on_success"),
                next_on_failure=step.get("next_on_failure"),
                timeout=step.get("timeout"))
                for step in steps],
            tags=list(template.tags))
        self.history.record(template_id, values, ok=True)
        return definition

    def usage(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.history.list(limit)
