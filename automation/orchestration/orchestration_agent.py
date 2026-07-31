"""Agents that execute orchestrated tasks."""

from __future__ import annotations

from typing import Any, Callable

from automation.orchestration.orchestration_models import OrchestrationTask


class OrchestrationAgent:
    """An executor capable of handling certain task kinds."""

    def __init__(self, agent_id: str, role: str, capabilities: list[str],
                 handler: Callable[[OrchestrationTask], Any] | None = None) -> None:
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.handler = handler

    def can_handle(self, kind: str) -> bool:
        return kind in self.capabilities

    def execute(self, task: OrchestrationTask) -> Any:
        if self.handler is None:
            raise RuntimeError(f"agent '{self.agent_id}' has no handler")
        return self.handler(task)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "capabilities": list(self.capabilities),
        }
