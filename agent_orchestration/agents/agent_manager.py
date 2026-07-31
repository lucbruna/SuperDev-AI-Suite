"""Agent lifecycle management (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import (AgentProfile, AgentStatus)
from agent_orchestration.orchestrator_registry import OrchestratorRegistry
from agent_orchestration.orchestrator_security import OrchestratorSecurity


class AgentManager:
    """Registration, status, permissions and agent picking."""

    def __init__(self, registry: OrchestratorRegistry | None = None,
                 security: OrchestratorSecurity | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.registry = registry or OrchestratorRegistry()
        self.security = security or OrchestratorSecurity()
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()

    def register(self, agent: AgentProfile) -> AgentProfile:
        self.registry.register_agent(agent)
        self.metrics.increment("ao.agents")
        self.events.publish(OrchestratorEventType.AGENT_REGISTERED,
                            {"agent_id": agent.agent_id, "name": agent.name,
                             "role": agent.role})
        return agent

    def unregister(self, agent_id: str) -> bool:
        if not self.registry.remove_agent(agent_id):
            return False
        self.metrics.increment("ao.agents", -1)
        self.events.publish(OrchestratorEventType.AGENT_REMOVED,
                            {"agent_id": agent_id})
        return True

    def get(self, agent_id: str) -> AgentProfile | None:
        return self.registry.get_agent(agent_id)

    def list(self) -> list[AgentProfile]:
        return self.registry.list_agents()

    def set_status(self, agent_id: str, status: AgentStatus) -> bool:
        agent = self.registry.get_agent(agent_id)
        if agent is None:
            return False
        agent.status = status
        self.events.publish(OrchestratorEventType.AGENT_STATUS_CHANGED,
                            {"agent_id": agent_id, "status": status.value})
        return True

    def grant_permission(self, agent_id: str, permission: str) -> bool:
        if self.registry.get_agent(agent_id) is None:
            return False
        self.security.grant(agent_id, permission)
        return True

    def can(self, agent_id: str, permission: str) -> bool:
        agent = self.registry.get_agent(agent_id)
        return bool(agent and agent.can(permission)) or \
            self.security.can(agent_id, permission)

    def pick_agent(self, capability: str) -> AgentProfile | None:
        for agent in self.registry.list_agents():
            if agent.status == AgentStatus.IDLE and \
                    agent.has_capability(capability):
                self.set_status(agent.agent_id, AgentStatus.BUSY)
                return agent
        return None

    def release(self, agent_id: str) -> bool:
        return self.set_status(agent_id, AgentStatus.IDLE)
