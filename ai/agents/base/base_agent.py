from __future__ import annotations

from typing import Any, Dict


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        self._agent_id = agent_id
        self._name = name or agent_id
        self._status: str = "idle"

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {"agent_id": self._agent_id, "status": "completed", "task": task}

    def to_dict(self) -> Dict[str, Any]:
        return {"agent_id": self._agent_id, "name": self._name, "status": self._status}
