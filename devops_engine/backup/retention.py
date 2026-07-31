"""Backup retention policy (Volume 37, Fase 5)."""

from __future__ import annotations

from devops_engine.devops_models import Snapshot
from devops_engine.devops_protocols import now


class RetentionPolicy:
    """Prunes old snapshots beyond a retention window."""

    def expired(self, snapshot: Snapshot, retention_days: float) -> bool:
        return (now() - snapshot.created_at) > float(retention_days) * 86400.0

    def prune(self, snapshots: list[Snapshot],
              keep: int = 30) -> list[Snapshot]:
        """Returns the snapshots that should be deleted."""
        ordered = sorted(snapshots, key=lambda item: item.created_at)
        if len(ordered) <= keep:
            return []
        return ordered[:len(ordered) - max(0, keep)]
