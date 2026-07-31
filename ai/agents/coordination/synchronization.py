from __future__ import annotations

from typing import Any


class Synchronization:
    """Synchronization primitives for agents."""

    def __init__(self) -> None:
        self._locks: dict[str, bool] = {}
        self._barriers: dict[str, list[str]] = {}

    def acquire_lock(self, resource: str, agent_id: str) -> bool:
        if self._locks.get(resource, False):
            return False
        self._locks[resource] = True
        return True

    def release_lock(self, resource: str) -> bool:
        if resource not in self._locks:
            return False
        self._locks[resource] = False
        return True

    def create_barrier(self, name: str, count: int) -> None:
        self._barriers[name] = []

    def wait_barrier(self, name: str, agent_id: str) -> bool:
        if name not in self._barriers:
            return False
        if agent_id not in self._barriers[name]:
            self._barriers[name].append(agent_id)
        return True

    def barrier_ready(self, name: str, total: int) -> bool:
        return len(self._barriers.get(name, [])) >= total

    def clear(self) -> None:
        self._locks.clear()
        self._barriers.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "locks": dict(self._locks),
            "barriers": {b: len(m) for b, m in self._barriers.items()},
        }
