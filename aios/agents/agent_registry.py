"""AgentRegistry: agent lookup, capability routing and dispatch."""
from __future__ import annotations

from typing import Any, Optional

from aios.agents.base_agent import BaseAgent


class AgentRegistry:
    """In-memory registry of AIOS agents."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> BaseAgent:
        if agent.name in self._agents:
            raise KeyError(f"agent {agent.name!r} already registered")
        self._agents[agent.name] = agent
        return agent

    def register_many(self, agents: list[BaseAgent]) -> list[BaseAgent]:
        for agent in agents:
            self.register(agent)
        return agents

    def get(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

    def names(self) -> list[str]:
        return sorted(self._agents)

    def agents(self) -> list[BaseAgent]:
        return [self._agents[name] for name in sorted(self._agents)]

    def find_by_capability(self, capability: str) -> list[BaseAgent]:
        return [agent for agent in self.agents() if agent.has_capability(capability)]

    def dispatch(self, name: str, input_data: Any, context: dict[str, Any] | None = None) -> Optional[dict[str, Any]]:
        agent = self.get(name)
        return agent.run(input_data, context) if agent is not None else None

    def run_for_capability(self, capability: str, input_data: Any, context: dict[str, Any] | None = None) -> Optional[dict[str, Any]]:
        matches = self.find_by_capability(capability)
        if not matches:
            return None
        return matches[0].run(input_data, context)

    def stats(self) -> dict[str, Any]:
        return {
            "total": len(self._agents),
            "agents": [agent.summary() for agent in self.agents()],
            "capabilities": sorted({cap for agent in self._agents.values() for cap in agent.capabilities}),
        }


def create_default_registry() -> AgentRegistry:
    """Instantiate and register the standard 13-agent swarm."""
    from aios.agents.agriculture import AgricultureAgent
    from aios.agents.analytics import AnalyticsAgent
    from aios.agents.avatar import AvatarAgent
    from aios.agents.developer import DeveloperAgent
    from aios.agents.director import DirectorAgent
    from aios.agents.finance import FinanceAgent
    from aios.agents.marketing import MarketingAgent
    from aios.agents.planner import PlannerAgent
    from aios.agents.research import ResearchAgent
    from aios.agents.security import SecurityAgent
    from aios.agents.testing import TestingAgent
    from aios.agents.video import VideoAgent
    from aios.agents.voice import VoiceAgent

    registry = AgentRegistry()
    registry.register_many(
        [
            DirectorAgent(),
            PlannerAgent(),
            ResearchAgent(),
            DeveloperAgent(),
            SecurityAgent(),
            TestingAgent(),
            MarketingAgent(),
            FinanceAgent(),
            AgricultureAgent(),
            VideoAgent(),
            VoiceAgent(),
            AvatarAgent(),
            AnalyticsAgent(),
        ]
    )
    director = registry.get("director")
    if isinstance(director, DirectorAgent):
        director.registry = registry
    return registry
