from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkflowDefinition:
    """Defines a workflow with metadata and steps."""

    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    triggers: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "steps": self.steps,
            "triggers": self.triggers,
            "tags": self.tags,
            "variables": self.variables,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
