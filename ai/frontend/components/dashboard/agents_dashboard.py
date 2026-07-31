"""
Agents Dashboard
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class AgentDashboardStatus(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class AgentDashboardInfo:
    id: str
    name: str
    status: AgentDashboardStatus
    tasks_completed: int = 0
    tasks_failed: int = 0
    uptime: float = 0
    last_active: str = ""


class AgentsDashboard:
    def __init__(self):
        self.agents: List[AgentDashboardInfo] = []
        
    def add_agent(self, agent: AgentDashboardInfo) -> None:
        self.agents.append(agent)
        
    def get_active_count(self) -> int:
        return sum(1 for a in self.agents if a.status == AgentDashboardStatus.ACTIVE)
        
    def get_stats(self) -> Dict[str, int]:
        stats = {}
        for status in AgentDashboardStatus:
            stats[status.value] = sum(1 for a in self.agents if a.status == status)
        return stats
        
    def render(self) -> Dict[str, Any]:
        return {
            "agents": [{"id": a.id, "name": a.name, "status": a.status.value} for a in self.agents],
            "activeCount": self.get_active_count(),
            "stats": self.get_stats(),
        }
