"""Snapshot management (Volume 37, Fase 5)."""

from __future__ import annotations

from devops_engine.devops_models import Snapshot
from devops_engine.devops_protocols import new_id, now


class SnapshotManager:
    """Creates point-in-time snapshots for backups."""

    def __init__(self) -> None:
        self._snapshots: dict[str, Snapshot] = {}

    def create(self, backup_id: str, name: str = "") -> Snapshot:
        snapshot = Snapshot(
            snapshot_id=new_id("snapshot"),
            backup_id=backup_id,
            name=name or f"snapshot-{backup_id[-6:]}",
            created_at=now(),
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def get(self, snapshot_id: str) -> Snapshot | None:
        return self._snapshots.get(snapshot_id)

    def list(self) -> list[Snapshot]:
        return list(self._snapshots.values())

    def count(self) -> int:
        return len(self._snapshots)
