from __future__ import annotations

import time
from typing import Any


class ActiveAgent:
    """An agent currently active in the system."""

    def __init__(self, agent_id: str, name: str, role: str = "", metadata: dict[str, Any] | None = None):
        self._agent_id = agent_id
        self._name = name
        self._role = role
        self._metadata = metadata or {}
        self._status: str = "idle"
        self._last_activity: float = time.time()
        self._created_at: float = time.time()

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return self._role

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value
        self._last_activity = time.time()

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    @property
    def last_activity(self) -> float:
        return self._last_activity

    @property
    def idle_time(self) -> float:
        return time.time() - self._last_activity

    def touch(self) -> None:
        self._last_activity = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "name": self._name,
            "role": self._role,
            "status": self._status,
            "idle_time": self.idle_time,
            "created_at": self._created_at,
        }


class ActiveAgents:
    """Registry of currently active agents."""

    def __init__(self):
        self._agents: dict[str, ActiveAgent] = {}

    @property
    def count(self) -> int:
        return len(self._agents)

    def register(self, agent_id: str, name: str, role: str = "", metadata: dict[str, Any] | None = None) -> ActiveAgent:
        agent = ActiveAgent(agent_id, name, role, metadata)
        self._agents[agent_id] = agent
        return agent

    def get(self, agent_id: str) -> ActiveAgent | None:
        return self._agents.get(agent_id)

    def set_status(self, agent_id: str, status: str) -> bool:
        agent = self._agents.get(agent_id)
        if agent is None:
            return False
        agent.status = status
        return True

    def remove(self, agent_id: str) -> bool:
        return self._agents.pop(agent_id, None) is not None

    def list_active(self) -> list[ActiveAgent]:
        return [a for a in self._agents.values() if a.status != "idle"]

    def list_idle(self) -> list[ActiveAgent]:
        return [a for a in self._agents.values() if a.status == "idle"]

    def clear(self) -> None:
        self._agents.clear()

    def to_dict_list(self) -> list[dict[str, Any]]:
        return [a.to_dict() for a in self._agents.values()]
