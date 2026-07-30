from __future__ import annotations

from typing import Any

from .database_tool import DatabaseTool


class Replication:
    """Database replication management."""

    def __init__(self, primary: DatabaseTool, replicas: list[DatabaseTool] | None = None):
        self._primary = primary
        self._replicas = replicas or []
        self._lag = 0.0

    def add_replica(self, replica: DatabaseTool) -> None:
        self._replicas.append(replica)

    def remove_replica(self, replica: DatabaseTool) -> None:
        self._replicas = [r for r in self._replicas if r is not replica]

    def sync(self) -> dict[str, Any]:
        synced = 0
        for replica in self._replicas:
            replica.execute("SELECT 1")
            synced += 1
        return {"synced": synced, "total_replicas": len(self._replicas)}

    def status(self) -> dict[str, Any]:
        return {
            "primary_connected": self._primary.is_connected,
            "replica_count": len(self._replicas),
            "lag_seconds": self._lag,
        }

    def measure_lag(self) -> float:
        return self._lag
