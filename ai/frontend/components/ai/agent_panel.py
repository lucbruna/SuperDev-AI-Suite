"""
AI Agent Panel
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class AgentType(Enum):
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    REVIEWER = "reviewer"
    DEPLOYER = "deployer"
    MONITOR = "monitor"


@dataclass
class AgentInfo:
    id: str
    name: str
    type: AgentType
    status: AgentStatus = AgentStatus.IDLE
    progress: float = 0.0
    current_task: str = ""
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentPanel:
    def __init__(self):
        self.agents: list[AgentInfo] = []
        self.selected_agent: AgentInfo | None = None
        self.listeners: list[Callable] = []

    def add_agent(self, agent: AgentInfo) -> None:
        self.agents.append(agent)
        self._emit("agent_added", {"agent": agent})

    def remove_agent(self, agent_id: str) -> bool:
        for i, a in enumerate(self.agents):
            if a.id == agent_id:
                self.agents.pop(i)
                self._emit("agent_removed", {"agentId": agent_id})
                return True
        return False

    def update_status(self, agent_id: str, status: AgentStatus, task: str = "") -> None:
        for a in self.agents:
            if a.id == agent_id:
                a.status = status
                if task:
                    a.current_task = task
                self._emit("agent_updated", {"agent": a})
                return

    def select(self, agent_id: str) -> AgentInfo | None:
        self.selected_agent = next((a for a in self.agents if a.id == agent_id), None)
        return self.selected_agent

    def get_by_type(self, agent_type: AgentType) -> list[AgentInfo]:
        return [a for a in self.agents if a.type == agent_type]

    def get_by_status(self, status: AgentStatus) -> list[AgentInfo]:
        return [a for a in self.agents if a.status == status]

    def on(self, event: str, callback: Callable) -> None:
        self.listeners.append({"event": event, "callback": callback})

    def _emit(self, event: str, data: dict[str, Any]) -> None:
        for l in self.listeners:
            if l["event"] == event:
                l["callback"](data)

    def render(self) -> dict[str, Any]:
        return {
            "agents": [{"id": a.id, "name": a.name, "type": a.type.value, "status": a.status.value, "progress": a.progress} for a in self.agents],
            "selectedId": self.selected_agent.id if self.selected_agent else None,
        }
