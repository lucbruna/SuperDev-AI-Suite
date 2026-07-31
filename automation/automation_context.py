"""Execution context for automation runs."""

from __future__ import annotations

import time
import uuid
from typing import Any


class AutomationContext:
    """Carries state and attributes across workflow steps."""

    def __init__(self, workflow_id: str, initial: dict[str, Any] | None = None) -> None:
        self.execution_id = str(uuid.uuid4())
        self.workflow_id = workflow_id
        self.created_at = time.time()
        self.attributes: dict[str, Any] = dict(initial or {})
        self.step_results: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def record_step(self, step_id: str, result: Any) -> None:
        self.step_results[step_id] = result

    def step_result(self, step_id: str) -> Any:
        return self.step_results.get(step_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "attributes": dict(self.attributes),
            "step_results": dict(self.step_results),
        }
