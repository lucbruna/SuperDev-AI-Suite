"""Hallmark runtime — execution state container for a skill run."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Runtime:
    """Tracks variables, step history, and status of one run."""

    status: str = "pending"
    variables: dict[str, Any] = field(default_factory=dict)
    steps: list[dict[str, Any]] = field(default_factory=list)

    def set(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def record_step(self, name: str, detail: dict[str, Any] | None = None) -> None:
        self.steps.append({"name": name, "detail": detail or {}})

    def finish(self) -> dict[str, Any]:
        self.status = "finished"
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "variable_count": len(self.variables),
            "step_count": len(self.steps),
        }
