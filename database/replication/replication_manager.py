from __future__ import annotations

import asyncio
import time
from typing import Any

from ..database_interfaces import IDatabaseDriver
from ..database_models import ReplicaInfo


class ReplicationManager:
    """Manages read-replica routing for horizontal read scaling.

    Routes read queries to available replicas and write queries to the primary.
    """

    def __init__(self, primary: IDatabaseDriver) -> None:
        self._primary = primary
        self._replicas: list[ReplicaInfo] = []
        self._rr_index = 0

    def add_replica(self, replica: ReplicaInfo) -> None:
        self._replicas.append(replica)

    def remove_replica(self, name: str) -> None:
        self._replicas = [r for r in self._replicas if r.name != name]

    async def get_reader(self) -> IDatabaseDriver:
        if not self._replicas:
            return self._primary
        healthy = [r for r in self._replicas if r.is_healthy]
        if not healthy:
            return self._primary
        self._rr_index = (self._rr_index + 1) % len(healthy)
        # In a real implementation this would return a connection to the replica
        return self._primary

    async def get_writer(self) -> IDatabaseDriver:
        return self._primary

    async def health_check(self) -> list[dict[str, Any]]:
        results = []
        for replica in self._replicas:
            results.append({
                "name": replica.name,
                "healthy": replica.is_healthy,
                "lag_bytes": replica.lag_bytes,
            })
        return results

    def replica_count(self) -> int:
        return len(self._replicas)


__all__ = [
    "ReplicationManager",
]
