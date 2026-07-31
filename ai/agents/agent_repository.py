from __future__ import annotations

from typing import Any


class AgentRepository:
    """Data repository for agent persistence."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}

    def save(self, agent_id: str, data: dict[str, Any]) -> None:
        self._data[agent_id] = data

    def load(self, agent_id: str) -> dict[str, Any] | None:
        return self._data.get(agent_id)

    def delete(self, agent_id: str) -> bool:
        return self._data.pop(agent_id, None) is not None

    def list_ids(self) -> list[str]:
        return list(self._data.keys())

    def count(self) -> int:
        return len(self._data)

    def clear(self) -> None:
        self._data.clear()
