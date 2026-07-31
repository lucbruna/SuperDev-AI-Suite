"""
Agent Service
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentConfig:
    id: str
    name: str
    agent_type: str = "coder"
    status: str = "idle"
    capabilities: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


class AgentService:
    def __init__(self):
        self.agents: list[AgentConfig] = []

    def list(self) -> list[AgentConfig]:
        return self.agents

    def get(self, agent_id: str) -> AgentConfig | None:
        return next((a for a in self.agents if a.id == agent_id), None)

    def create(self, name: str, agent_type: str = "coder") -> AgentConfig:
        import uuid
        agent = AgentConfig(id=str(uuid.uuid4()), name=name, agent_type=agent_type)
        self.agents.append(agent)
        return agent

    def update_status(self, agent_id: str, status: str) -> None:
        agent = self.get(agent_id)
        if agent:
            agent.status = status

    def render(self) -> dict[str, Any]:
        return {"agents": [{"id": a.id, "name": a.name, "status": a.status} for a in self.agents]}
