from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


class VectorBackup:
    """Create and manage vector index backups."""

    def __init__(self):
        self._backups: dict[str, dict[str, Any]] = {}

    def create_backup(self, vectors: dict[str, list[float]], metadata: dict[str, Any] | None = None) -> str:
        backup_id = f"backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self._backups[backup_id] = {
            "id": backup_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vector_count": len(vectors),
            "vectors": {k: v for k, v in vectors.items()},
            "metadata": metadata or {},
        }
        return backup_id

    def list_backups(self) -> list[dict[str, Any]]:
        return [
            {"id": b["id"], "timestamp": b["timestamp"], "vector_count": b["vector_count"]}
            for b in self._backups.values()
        ]

    def get_backup(self, backup_id: str) -> dict[str, Any] | None:
        return self._backups.get(backup_id)
