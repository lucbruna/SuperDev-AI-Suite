from __future__ import annotations

from typing import Any, Dict, List, Optional


class AgentRepository:
    """Data repository for agent persistence."""

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}

    def save(self, agent_id: str, data: Dict[str, Any]) -> None:
        self._data[agent_id] = data

    def load(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._data.get(agent_id)

    def delete(self, agent_id: str) -> bool:
        return self._data.pop(agent_id, None) is not None

    def list_ids(self) -> List[str]:
        return list(self._data.keys())

    def count(self) -> int:
        return len(self._data)

    def clear(self) -> None:
        self._data.clear()
