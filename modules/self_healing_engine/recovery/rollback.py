"""Rollback: restore state from a snapshot."""
from __future__ import annotations

from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.recovery.snapshot import Snapshot, SnapshotManager


class RollbackManager:
    """Restores healing state from snapshots."""

    def __init__(self, snapshots: SnapshotManager | None = None) -> None:
        self._snapshots = snapshots or SnapshotManager()

    def rollback(self, snapshot: Snapshot, ctx: HealingContext) -> bool:
        ctx.set_artifact("rollback_snapshot", snapshot.to_dict())
        ctx.publish(
            "recovery.rolled_back",
            {"id": snapshot.id, "kind": snapshot.kind},
        )
        return True

    def rollback_latest(
        self, ctx: HealingContext, kind: str | None = None
    ) -> bool:
        snapshot = self._snapshots.latest(kind)
        if snapshot is None:
            return False
        return self.rollback(snapshot, ctx)
