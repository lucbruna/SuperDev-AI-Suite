"""Replication manager."""

from __future__ import annotations

import time
from typing import Any


class ReplicationManager:
    def __init__(self) -> None:
        self._replications: dict[str, dict[str, Any]] = {}

    def setup(self, source: str, target: str, mode: str = "async") -> dict[str, Any]:
        replication = {
            "source": source,
            "target": target,
            "mode": mode,
            "status": "active",
            "lag_ms": 0,
            "last_sync": time.time(),
        }
        self._replications[f"{source}->{target}"] = replication
        return replication

    def get_status(self, source: str, target: str) -> dict[str, Any]:
        key = f"{source}->{target}"
        return self._replications.get(key, {"error": "not_found"})

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._replications.values())

    def pause(self, source: str, target: str) -> bool:
        key = f"{source}->{target}"
        if key in self._replications:
            self._replications[key]["status"] = "paused"
            return True
        return False

    def resume(self, source: str, target: str) -> bool:
        key = f"{source}->{target}"
        if key in self._replications:
            self._replications[key]["status"] = "active"
            return True
        return False

    def count(self) -> int:
        return len(self._replications)
