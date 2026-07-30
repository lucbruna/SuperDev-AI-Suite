from __future__ import annotations

from typing import Any


class Rollback:
    """Manages deployment snapshots and rollbacks."""

    def __init__(self) -> None:
        self._snapshots: dict[str, dict[str, Any]] = {}

    def create_snapshot(self, name: str, config: dict[str, Any]) -> str:
        self._snapshots[name] = {"name": name, "config": config}
        return name

    def get_snapshot(self, name: str) -> dict[str, Any] | None:
        return self._snapshots.get(name)

    @property
    def snapshot_count(self) -> int:
        return len(self._snapshots)

    def rollback_to(self, name: str) -> dict[str, Any]:
        snapshot = self._snapshots.get(name)
        if snapshot is None:
            return {"status": "not_found"}
        return {"status": "rolled_back", "snapshot": snapshot["name"]}

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshots": list(self._snapshots.values()),
            "snapshot_count": self.snapshot_count,
        }
