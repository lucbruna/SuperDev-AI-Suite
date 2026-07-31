from __future__ import annotations

import time
from typing import Any


class NodeSync:
    """Synchronizes data between individual nodes."""

    def __init__(self):
        self._nodes: dict[str, dict[str, Any]] = {}
        self._sync_log: list[dict[str, Any]] = []

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    def register(self, node_id: str, version: str = "1.0") -> None:
        self._nodes[node_id] = {"version": version, "last_sync": 0.0, "status": "active"}

    def unregister(self, node_id: str) -> bool:
        return self._nodes.pop(node_id, None) is not None

    def record_sync(self, source: str, target: str, status: str = "ok") -> None:
        self._sync_log.append({
            "source": source,
            "target": target,
            "status": status,
            "timestamp": time.time(),
        })
        if source in self._nodes:
            self._nodes[source]["last_sync"] = time.time()
        if target in self._nodes:
            self._nodes[target]["last_sync"] = time.time()

    def last_sync(self, node_id: str) -> float | None:
        node = self._nodes.get(node_id)
        return node["last_sync"] if node else None

    def sync_status(self, node_id: str) -> str | None:
        node = self._nodes.get(node_id)
        return node["status"] if node else None

    def list_nodes(self) -> list[str]:
        return list(self._nodes.keys())

    def get_sync_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return list(self._sync_log[-limit:])

    def clear(self) -> None:
        self._nodes.clear()
        self._sync_log.clear()
