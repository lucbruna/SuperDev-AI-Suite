"""BaseAgent: shared foundation for every AIOS agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentConfig:
    name: str
    role: str
    capabilities: list[str] = field(default_factory=list)
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    """Deterministic agent base: uniform ``run`` contract with history."""

    def __init__(
        self,
        name: str,
        role: str,
        capabilities: list[str] | None = None,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.role = role
        self.capabilities = list(capabilities or [])
        self.description = description
        self.metadata = dict(metadata or {})
        self.history: list[dict[str, Any]] = []
        self._tasks = 0

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        raise NotImplementedError(f"{type(self).__name__} must implement process()")

    def run(self, input_data: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
        self._tasks += 1
        entry: dict[str, Any] = {
            "task_id": f"{self.name}-{self._tasks:04d}",
            "agent": self.name,
            "role": self.role,
            "input": input_data,
            "status": "completed",
        }
        try:
            entry["result"] = self.process(input_data, dict(context or {}))
        except Exception as exc:
            entry["status"] = "failed"
            entry["error"] = str(exc)
        self.history.append(entry)
        return entry

    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": list(self.capabilities),
            "description": self.description,
            "tasks": self._tasks,
        }
