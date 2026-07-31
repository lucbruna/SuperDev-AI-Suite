from __future__ import annotations

from typing import Any


class AgentContext:
    """Execution context for an agent."""

    def __init__(self, agent_id: str) -> None:
        self._agent_id = agent_id
        self._variables: dict[str, Any] = {}
        self._task_id: str | None = None

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def task_id(self) -> str | None:
        return self._task_id

    @task_id.setter
    def task_id(self, value: str | None) -> None:
        self._task_id = value

    def set(self, key: str, value: Any) -> None:
        self._variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._variables.get(key, default)

    def clear(self) -> None:
        self._variables.clear()
        self._task_id = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "task_id": self._task_id,
            "variables": dict(self._variables),
        }
