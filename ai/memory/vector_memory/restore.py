from __future__ import annotations

import json

from .backup import Backup
from .embedding_repository import EmbeddingRepository


class Restore:
    """Restores vector memory data from backups."""

    def __init__(self, repository: EmbeddingRepository, backup: Backup):
        self._repository = repository
        self._backup = backup
        self._restore_count: int = 0

    @property
    def restore_count(self) -> int:
        return self._restore_count

    def restore_from_backup(self, backup_id: str, clear_existing: bool = False) -> int:
        entries = self._backup.get_backup(backup_id)
        if entries is None:
            raise ValueError(f"Backup not found: {backup_id}")
        if clear_existing:
            self._repository.clear()
        count = 0
        for entry in entries:
            self._repository.store(entry.vector_id, entry.vector, entry.metadata)
            count += 1
        self._restore_count += 1
        return count

    def restore_from_json(self, json_data: str, clear_existing: bool = False) -> int:
        raw = json.loads(json_data)
        if not isinstance(raw, list):
            raise ValueError("JSON data must be a list of entries")
        if clear_existing:
            self._repository.clear()
        count = 0
        for item in raw:
            self._repository.store(item["vector_id"], item["vector"], item.get("metadata", {}))
            count += 1
        self._restore_count += 1
        return count

    def restore_latest(self, clear_existing: bool = False) -> int:
        backups = self._backup.list_backups()
        if not backups:
            raise ValueError("No backups available")
        return self.restore_from_backup(backups[-1], clear_existing)
