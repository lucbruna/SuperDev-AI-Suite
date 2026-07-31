"""
Agent Store
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class AgentState:
    agents: List[Dict[str, Any]] = field(default_factory=list)
    selected_id: Optional[str] = None


class AgentStore:
    def __init__(self):
        self.state = AgentState()
        self.listeners: List = []
        
    def set_agents(self, agents: List[Dict[str, Any]]) -> None:
        self.state.agents = agents
        self._notify()
        
    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> None:
        for agent in self.state.agents:
            if agent.get("id") == agent_id:
                agent.update(updates)
                break
        self._notify()
        
    def _notify(self) -> None:
        for cb in self.listeners:
            cb(self.state)
            
    def on_change(self, callback) -> None:
        self.listeners.append(callback)
        
    def render(self) -> Dict[str, Any]:
        return {"agents": self.state.agents, "selectedId": self.state.selected_id}
