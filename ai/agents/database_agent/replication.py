from __future__ import annotations

from typing import Any

REPLICATION_MODES = {"sync", "async"}


class Replication:
    """Manages database replication configuration."""

    def __init__(self) -> None:
        self._mode: str = "async"
        self._replicas: dict[str, dict[str, Any]] = {}

    def configure(self, mode: str, replicas: int = 1) -> str:
        mode = mode.lower()
        self._mode = mode if mode in REPLICATION_MODES else "async"
        return self._mode

    def add_replica(self, name: str, lag_seconds: float = 0) -> str:
        self._replicas[name] = {
            "name": name,
            "lag_seconds": lag_seconds,
            "status": "healthy",
        }
        return name

    def remove_replica(self, name: str) -> bool:
        if name in self._replicas:
            del self._replicas[name]
            return True
        return False

    def list_replicas(self) -> list[dict[str, Any]]:
        return list(self._replicas.values())

    @property
    def replica_count(self) -> int:
        return len(self._replicas)

    def get_status(self) -> dict[str, Any]:
        return {
            "mode": self._mode,
            "replicas": self.replica_count,
            "healthy": sum(1 for r in self._replicas.values() if r["status"] == "healthy"),
        }

    @property
    def replication_mode(self) -> str:
        return self._mode

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self._mode,
            "replicas": list(self._replicas.values()),
            "replica_count": self.replica_count,
        }
