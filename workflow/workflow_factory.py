from __future__ import annotations

import time
from typing import Any

from .workflow_models import (
    WorkflowDefinition,
    WorkflowStep,
    WorkflowTrigger,
    WorkflowStatus,
    StepStatus,
)


class WorkflowFactory:
    """Factory for creating workflow definitions."""

    def from_dict(self, data: dict[str, Any]) -> WorkflowDefinition:
        steps = [
            WorkflowStep(
                id=s.get("id", f"step_{i}"),
                name=s.get("name", s.get("id", f"step_{i}")),
                action=s.get("action", ""),
                depends_on=s.get("depends_on", []),
                max_retries=s.get("max_retries", 3),
                timeout=s.get("timeout", 300.0),
            )
            for i, s in enumerate(data.get("steps", []))
        ]
        triggers = [
            WorkflowTrigger(type=t["type"], config=t.get("config", {}))
            for t in data.get("triggers", [])
        ]
        return WorkflowDefinition(
            id=data.get("id", ""),
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            steps=steps,
            triggers=triggers,
            tags=data.get("tags", []),
            created_at=time.time(),
            updated_at=time.time(),
        )

    def create_simple(
        self, name: str, actions: list[str]
    ) -> WorkflowDefinition:
        steps = [
            WorkflowStep(
                id=f"step_{i}",
                name=f"Step {i + 1}: {action}",
                action=action,
            )
            for i, action in enumerate(actions)
        ]
        return WorkflowDefinition(
            id=f"wf_{int(time.time())}",
            name=name,
            steps=steps,
            created_at=time.time(),
            updated_at=time.time(),
        )
