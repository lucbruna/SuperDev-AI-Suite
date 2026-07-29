"""
Agent Registry - Central registry for all AI agents
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import Agent, AgentStatus


class AgentRegistry:
    """Registry for managing agent metadata and state"""

    def __init__(self):
        self._agents: Dict[UUID, Agent] = {}
        self._by_name: Dict[str, UUID] = {}

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        self._agents.clear()
        self._by_name.clear()

    async def register(self, agent: Agent) -> None:
        self._agents[agent.id] = agent
        self._by_name[agent.name] = agent.id

    async def unregister(self, agent_id: UUID) -> bool:
        agent = self._agents.pop(agent_id, None)
        if agent:
            self._by_name.pop(agent.name, None)
            return True
        return False

    def get(self, agent_id: UUID) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def get_by_name(self, name: str) -> Optional[Agent]:
        agent_id = self._by_name.get(name)
        if agent_id:
            return self._agents.get(agent_id)
        return None

    def list(self, status: Optional[AgentStatus] = None) -> List[Agent]:
        agents = list(self._agents.values())
        if status:
            agents = [a for a in agents if a.status == status]
        return sorted(agents, key=lambda a: a.name)

    def list_by_capability(self, capability: str) -> List[Agent]:
        return [a for a in self._agents.values() if capability in a.capabilities]

    def list_by_permission(self, permission: str) -> List[Agent]:
        return [a for a in self._agents.values() if permission in a.permissions]

    def count(self) -> int:
        return len(self._agents)

    def get_stats(self) -> Dict[str, Any]:
        status_counts = {}
        for agent in self._agents.values():
            status_counts[agent.status.value] = status_counts.get(agent.status.value, 0) + 1

        return {
            "total": len(self._agents),
            "by_status": status_counts,
            "capabilities": self._get_capability_stats(),
        }

    def _get_capability_stats(self) -> Dict[str, int]:
        stats = {}
        for agent in self._agents.values():
            for cap in agent.capabilities:
                stats[cap] = stats.get(cap, 0) + 1
        return stats