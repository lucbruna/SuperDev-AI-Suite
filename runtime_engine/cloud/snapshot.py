from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any


class SnapshotManager:
    def __init__(self):
        self._snapshots: dict[str, dict[str, Any]] = {}

    async def create(self, vm_id: str, name: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        snap_id = f"snap_{uuid.uuid4().hex[:12]}"
        self._snapshots[snap_id] = {
            "id": snap_id,
            "vm_id": vm_id,
            "name": name or f"snapshot_{snap_id[:8]}",
            "metadata": metadata or {},
            "size_mb": 128 + hash(snap_id) % 256,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat(),
        }
        return self._snapshots[snap_id]

    async def restore(self, snap_id: str, target_vm_id: str) -> dict[str, Any]:
        snap = self._snapshots.get(snap_id)
        if not snap:
            return {"error": "Snapshot not found"}
        return {"status": "restored", "snapshot_id": snap_id, "target_vm_id": target_vm_id, "restored_at": datetime.utcnow().isoformat()}

    async def delete(self, snap_id: str) -> bool:
        return self._snapshots.pop(snap_id, None) is not None

    async def list(self, vm_id: str | None = None) -> list[dict[str, Any]]:
        snaps = list(self._snapshots.values())
        if vm_id:
            snaps = [s for s in snaps if s["vm_id"] == vm_id]
        return sorted(snaps, key=lambda s: s["created_at"], reverse=True)

    async def get(self, snap_id: str) -> dict[str, Any] | None:
        return self._snapshots.get(snap_id)

    async def clone_vm(self, snap_id: str, new_name: str) -> dict[str, Any]:
        snap = self._snapshots.get(snap_id)
        if not snap:
            return {"error": "Snapshot not found"}
        new_vm_id = f"vm_clone_{uuid.uuid4().hex[:12]}"
        return {
            "vm_id": new_vm_id,
            "name": new_name,
            "source_snapshot": snap_id,
            "source_vm": snap["vm_id"],
            "status": "created",
        }

    async def get_stats(self) -> dict[str, Any]:
        total = len(self._snapshots)
        total_size_mb = sum(s["size_mb"] for s in self._snapshots.values())
        return {"total_snapshots": total, "total_size_mb": total_size_mb, "avg_size_mb": round(total_size_mb / max(total, 1), 1)}