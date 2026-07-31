"""
Agent Service
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    id: str
    name: str
    agent_type: str = "coder"
    status: str = "idle"
    capabilities: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class AgentService:
    def __init__(self):
        self.agents: List[AgentConfig] = []
        
    def list(self) -> List[AgentConfig]:
        return self.agents
        
    def get(self, agent_id: str) -> Optional[AgentConfig]:
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
            
    def render(self) -> Dict[str, Any]:
        return {"agents": [{"id": a.id, "name": a.name, "status": a.status} for a in self.agents]}
