"""Agent subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.agents.agent_factory import AgentFactory
from agent_orchestration.agents.agent_loader import AgentLoader
from agent_orchestration.agents.agent_manager import AgentManager
from agent_orchestration.orchestrator_events import OrchestratorEvents
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import (AgentProfile, AgentStatus)
from agent_orchestration.orchestrator_registry import OrchestratorRegistry


class AgentEngine:
    """Facade over agent lifecycle, factory and loader."""

    def __init__(self, manager: AgentManager | None = None,
                 factory: AgentFactory | None = None,
                 loader: AgentLoader | None = None,
                 registry: OrchestratorRegistry | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()
        self.registry = registry or OrchestratorRegistry()
        self.manager = manager or AgentManager(
            registry=self.registry, events=self.events,
            metrics=self.metrics)
        self.factory = factory or AgentFactory()
        self.loader = loader or AgentLoader()

    def register(self, agent: AgentProfile) -> AgentProfile:
        return self.manager.register(agent)

    def unregister(self, agent_id: str) -> bool:
        return self.manager.unregister(agent_id)

    def get(self, agent_id: str) -> AgentProfile | None:
        return self.manager.get(agent_id)

    def list(self) -> list[AgentProfile]:
        return self.manager.list()

    def set_status(self, agent_id: str, status: AgentStatus) -> bool:
        return self.manager.set_status(agent_id, status)

    def can(self, agent_id: str, permission: str) -> bool:
        return self.manager.can(agent_id, permission)

    def pick_agent(self, capability: str) -> AgentProfile | None:
        return self.manager.pick_agent(capability)

    def release(self, agent_id: str) -> bool:
        return self.manager.release(agent_id)

    def create(self, role: str, name: str = "") -> AgentProfile:
        agent = self.factory.create(role, name)
        return self.register(agent)

    def create_team(self, roles: list[str]) -> list[AgentProfile]:
        return [self.create(role) for role in roles]

    def create_coding_team(self) -> list[AgentProfile]:
        return self.create_team(["coding", "testing", "security", "data",
                                 "devops", "documentation"])

    def load_from_dict(self, data: dict) -> list[AgentProfile]:
        return self.loader.load_from_dict(data)

    def load_from_list(self, items: list[dict]) -> list[AgentProfile]:
        return self.loader.load_from_list(items)

    def stats(self) -> dict[str, Any]:
        by_role: dict[str, int] = {}
        for agent in self.list():
            by_role[agent.role] = by_role.get(agent.role, 0) + 1
        return {
            "agents": len(self.list()),
            "by_role": by_role,
            "metrics": self.metrics.snapshot()["counters"],
        }
