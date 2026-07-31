from __future__ import annotations

from typing import Any

from .agent_registry import AgentRegistry


class AgentRouter:
    """Routes tasks to appropriate agents."""

    def __init__(self) -> None:
        self._routes: dict[str, str] = {}

    @property
    def route_count(self) -> int:
        return len(self._routes)

    def add_route(self, task_type: str, agent_id: str) -> None:
        self._routes[task_type] = agent_id

    def remove_route(self, task_type: str) -> bool:
        return self._routes.pop(task_type, None) is not None

    def route(self, task: dict[str, Any], registry: AgentRegistry) -> str | None:
        task_type = task.get("type", "")
        agent_id = self._routes.get(task_type)
        if agent_id and registry.get_agent(agent_id):
            return agent_id
        return None

    def clear(self) -> None:
        self._routes.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"routes": dict(self._routes)}
