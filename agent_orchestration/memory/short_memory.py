"""Short-term memory: recent entries per agent (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_protocols import now


class ShortMemory:
    """Keeps the most recent entries per agent, dropping the oldest."""

    def __init__(self, capacity: int = 50) -> None:
        self.capacity = max(1, capacity)
        self._entries: dict[str, list[dict[str, Any]]] = {}

    def add(self, agent_id: str, entry: str,
            payload: dict[str, Any] | None = None) -> dict[str, Any]:
        record = {"entry": entry, "payload": dict(payload or {}),
                  "created_at": now()}
        queue = self._entries.setdefault(agent_id, [])
        queue.append(record)
        if len(queue) > self.capacity:
            del queue[:len(queue) - self.capacity]
        return record

    def recent(self, agent_id: str, limit: int = 10) -> list[dict[str, Any]]:
        return list(self._entries.get(agent_id, [])[-limit:])

    def count(self, agent_id: str) -> int:
        return len(self._entries.get(agent_id, []))

    def clear(self, agent_id: str | None = None) -> None:
        if agent_id is None:
            self._entries.clear()
        else:
            self._entries.pop(agent_id, None)

    def total(self) -> int:
        return sum(len(queue) for queue in self._entries.values())
