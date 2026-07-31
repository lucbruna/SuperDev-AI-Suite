"""Snapshot manager."""

from __future__ import annotations

import time
from typing import Any


class SnapshotManager:
    def __init__(self) -> None:
        self._snapshots: dict[str, dict[str, Any]] = {}

    def create(self, name: str, source: str, description: str = "") -> dict[str, Any]:
        snapshot = {
            "name": name,
            "source": source,
            "description": description,
            "size_mb": 200,
            "status": "completed",
            "created_at": time.time(),
        }
        self._snapshots[name] = snapshot
        return snapshot

    def get(self, name: str) -> dict[str, Any]:
        return self._snapshots.get(name, {"error": "not_found"})

    def restore(self, name: str) -> dict[str, Any]:
        if name not in self._snapshots:
            return {"error": "not_found"}
        return {"snapshot": name, "status": "restored"}

    def delete(self, name: str) -> bool:
        if name in self._snapshots:
            del self._snapshots[name]
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._snapshots.values())

    def count(self) -> int:
        return len(self._snapshots)
