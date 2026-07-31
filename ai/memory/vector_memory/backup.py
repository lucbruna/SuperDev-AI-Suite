from __future__ import annotations

import json
import time
from typing import Any

from .embedding_repository import EmbeddingRepository


class BackupEntry:
    """A single backup entry containing vector data and metadata."""

    def __init__(self, vector_id: str, vector: list[float], metadata: dict[str, Any]):
        self._vector_id = vector_id
        self._vector = list(vector)
        self._metadata = dict(metadata)

    @property
    def vector_id(self) -> str:
        return self._vector_id

    @property
    def vector(self) -> list[float]:
        return list(self._vector)

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector_id": self._vector_id,
            "vector": list(self._vector),
            "metadata": dict(self._metadata),
        }


class Backup:
    """Creates backups of vector memory data."""

    def __init__(self, repository: EmbeddingRepository):
        self._repository = repository
        self._backups: dict[str, list[BackupEntry]] = {}

    @property
    def backup_count(self) -> int:
        return len(self._backups)

    def create_backup(self, name: str | None = None) -> str:
        backup_id = name or f"backup_{int(time.time())}"
        entries = []
        for entry in self._repository.list_entries():
            entries.append(BackupEntry(entry.vector_id, entry.vector, entry.metadata))
        self._backups[backup_id] = entries
        return backup_id

    def get_backup(self, backup_id: str) -> list[BackupEntry] | None:
        entries = self._backups.get(backup_id)
        if entries is None:
            return None
        return list(entries)

    def list_backups(self) -> list[str]:
        return list(self._backups.keys())

    def delete_backup(self, backup_id: str) -> bool:
        return self._backups.pop(backup_id, None) is not None

    def export_to_json(self, backup_id: str) -> str | None:
        entries = self.get_backup(backup_id)
        if entries is None:
            return None
        return json.dumps([e.to_dict() for e in entries], indent=2)

    def clear(self) -> None:
        self._backups.clear()
