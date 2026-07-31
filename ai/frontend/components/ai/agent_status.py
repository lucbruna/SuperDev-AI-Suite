"""
Agent Status Component
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class StatusLevel(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class AgentStatusInfo:
    agent_id: str
    name: str
    status: str = "idle"
    health: StatusLevel = StatusLevel.HEALTHY
    uptime: float = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    current_task: str = ""
    last_error: str = ""
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


class AgentStatus:
    def __init__(self):
        self.statuses: Dict[str, AgentStatusInfo] = {}
        
    def update(self, agent_id: str, **kwargs) -> None:
        if agent_id not in self.statuses:
            self.statuses[agent_id] = AgentStatusInfo(agent_id=agent_id, name=kwargs.get("name", agent_id))
        for k, v in kwargs.items():
            if hasattr(self.statuses[agent_id], k):
                setattr(self.statuses[agent_id], k, v)
                
    def get(self, agent_id: str) -> Optional[AgentStatusInfo]:
        return self.statuses.get(agent_id)
        
    def get_overall_health(self) -> StatusLevel:
        if not self.statuses:
            return StatusLevel.UNKNOWN
        levels = [s.health for s in self.statuses.values()]
        if StatusLevel.CRITICAL in levels:
            return StatusLevel.CRITICAL
        if StatusLevel.WARNING in levels:
            return StatusLevel.WARNING
        return StatusLevel.HEALTHY
        
    def render(self) -> Dict[str, Any]:
        return {
            "statuses": {k: {"status": v.status, "health": v.health.value} for k, v in self.statuses.items()},
            "overallHealth": self.get_overall_health().value,
        }
