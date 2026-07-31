from __future__ import annotations

from typing import Any


class AgentModel:
    """Base data model for agents."""

    def __init__(self, agent_id: str, agent_type: str, name: str = "") -> None:
        self._agent_id = agent_id
        self._agent_type = agent_type
        self._name = name or agent_id
        self._status: str = "idle"
        self._metadata: dict[str, Any] = {}

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def agent_type(self) -> str:
        return self._agent_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def get_metadata(self, key: str) -> Any | None:
        return self._metadata.get(key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "agent_type": self._agent_type,
            "name": self._name,
            "status": self._status,
            "metadata": dict(self._metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentModel:
        model = cls(data["agent_id"], data["agent_type"], data.get("name", ""))
        model._status = data.get("status", "idle")
        model._metadata = data.get("metadata", {})
        return model


class TaskModel:
    """Data model for agent tasks."""

    def __init__(self, task_id: str, task_type: str, payload: dict[str, Any] | None = None) -> None:
        self._task_id = task_id
        self._task_type = task_type
        self._payload = payload or {}

    @property
    def task_id(self) -> str:
        return self._task_id

    @property
    def task_type(self) -> str:
        return self._task_type

    @property
    def payload(self) -> dict[str, Any]:
        return dict(self._payload)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self._task_id,
            "task_type": self._task_type,
            "payload": dict(self._payload),
        }
