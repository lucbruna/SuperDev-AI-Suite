"""AI agent health checks."""
from __future__ import annotations
from typing import Any, Dict, List

class AgentCheck:
    def __init__(self) -> None:
        self._agents: Dict[str, Dict[str, Any]] = {}
    def register(self, agent_id: str, config: Dict[str, Any]) -> None:
        self._agents[agent_id] = config
    def check(self, agent_id: str) -> Dict[str, Any]:
        agent = self._agents.get(agent_id)
        if not agent:
            return {"agent": agent_id, "status": "not_found"}
        return {"agent": agent_id, "status": "healthy", "type": agent.get("type", "unknown")}
    def check_all(self) -> List[Dict[str, Any]]:
        return [self.check(aid) for aid in self._agents]
    def list_agents(self) -> List[str]:
        return list(self._agents.keys())
    def remove(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False
