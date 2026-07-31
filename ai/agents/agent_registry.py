from __future__ import annotations

from typing import Any


class AgentRegistry:
    """Registry of all available agents."""

    def __init__(self) -> None:
        self._agents: dict[str, dict[str, Any]] = {}

    @property
    def agent_count(self) -> int:
        return len(self._agents)

    @property
    def agent_ids(self) -> list[str]:
        return list(self._agents.keys())

    def register(self, agent_id: str, metadata: dict[str, Any]) -> None:
        self._agents[agent_id] = metadata

    def unregister(self, agent_id: str) -> bool:
        return self._agents.pop(agent_id, None) is not None

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        return self._agents.get(agent_id)

    def find_by_type(self, agent_type: str) -> list[str]:
        return [aid for aid, meta in self._agents.items() if meta.get("type") == agent_type]

    def clear(self) -> None:
        self._agents.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"count": self.agent_count, "agents": dict(self._agents)}
