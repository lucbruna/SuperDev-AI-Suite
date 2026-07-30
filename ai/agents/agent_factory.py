from __future__ import annotations

from typing import Any, Dict, Optional

from .agent_registry import AgentRegistry


class AgentFactory:
    """Creates agent instances and registers them."""

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    def create_agent(self, agent_id: str, agent_type: str, config: Optional[Dict[str, Any]] = None) -> bool:
        agent = {"id": agent_id, "type": agent_type, "config": config or {}}
        self._registry.register(agent_id, agent)
        return True

    def create_batch(self, agents: Dict[str, str]) -> int:
        count = 0
        for agent_id, agent_type in agents.items():
            if self.create_agent(agent_id, agent_type):
                count += 1
        return count

    def remove_agent(self, agent_id: str) -> bool:
        return self._registry.unregister(agent_id)
