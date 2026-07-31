"""Data models for workflow templates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TemplateParameter:
    """A configurable variable of a workflow template."""

    name: str
    required: bool = False
    default: Any = None
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "required": self.required,
                "default": self.default, "description": self.description}


@dataclass
class WorkflowTemplate:
    """A reusable workflow definition with parameter placeholders.

    Steps use ``{{param}}`` placeholders that are substituted on
    instantiation, e.g. ``{"action": "api.call", "params": {"url": "{{url}}"}}``.
    """

    template_id: str
    name: str
    description: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    parameters: list[TemplateParameter] = field(default_factory=list)
    category: str = "general"  # business | developer | finance | support
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "parameters": [p.to_dict() for p in self.parameters],
            "category": self.category,
            "version": self.version,
            "tags": list(self.tags),
        }
