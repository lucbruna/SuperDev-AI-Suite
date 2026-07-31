from __future__ import annotations

from typing import Any


class LoadBalancer:
    """Balances workload across agents."""

    def __init__(self) -> None:
        self._load: dict[str, int] = {}

    def register(self, agent_id: str) -> None:
        if agent_id not in self._load:
            self._load[agent_id] = 0

    def assign(self, agent_id: str, weight: int = 1) -> None:
        self._load[agent_id] = self._load.get(agent_id, 0) + weight

    def complete(self, agent_id: str, weight: int = 1) -> None:
        current = self._load.get(agent_id, 0)
        self._load[agent_id] = max(0, current - weight)

    def get_load(self, agent_id: str) -> int:
        return self._load.get(agent_id, 0)

    def get_least_loaded(self) -> str | None:
        if not self._load:
            return None
        return min(self._load, key=self._load.get)

    def clear(self) -> None:
        self._load.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"loads": dict(self._load)}
