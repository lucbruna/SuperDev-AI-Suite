"""Agent registry wrapper (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import (AgentProfile, AgentStatus)
from agent_orchestration.orchestrator_registry import OrchestratorRegistry


class AgentRegistry:
    """Thin wrapper over OrchestratorRegistry with role/capability queries."""

    def __init__(self, registry: OrchestratorRegistry | None = None) -> None:
        self._registry = registry or OrchestratorRegistry()

    def register(self, agent: AgentProfile) -> None:
        self._registry.register_agent(agent)

    def get(self, agent_id: str) -> AgentProfile | None:
        return self._registry.get_agent(agent_id)

    def list(self) -> list[AgentProfile]:
        return self._registry.list_agents()

    def remove(self, agent_id: str) -> bool:
        return self._registry.remove_agent(agent_id)

    def count(self) -> int:
        return self._registry.count_agents()

    def by_role(self, role: str) -> list[AgentProfile]:
        return [agent for agent in self.list() if agent.role == role]

    def by_capability(self, capability: str) -> list[AgentProfile]:
        return [agent for agent in self.list()
                if agent.has_capability(capability)]

    def available(self) -> list[AgentProfile]:
        return [agent for agent in self.list()
                if agent.status == AgentStatus.IDLE]
