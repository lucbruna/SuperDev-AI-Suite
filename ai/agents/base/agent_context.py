from __future__ import annotations

from typing import Any


class AgentContext:
    """Contextual information for agent execution."""

    def __init__(self, agent_id: str) -> None:
        self._agent_id = agent_id
        self._data: dict[str, Any] = {}
        self._parent: str | None = None

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def parent(self) -> str | None:
        return self._parent

    @parent.setter
    def parent(self, value: str | None) -> None:
        self._parent = value

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def clear(self) -> None:
        self._data.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"agent_id": self._agent_id, "parent": self._parent, "data": dict(self._data)}
