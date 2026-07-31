from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from ..knowledge_interfaces import MemoryStore
from ..knowledge_models import MemoryRecord


class MemoryCleanup:
    """Prunes memory records based on age, importance, and capacity."""

    def __init__(self, store: MemoryStore) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.cleanup")
        self._store = store

    def prune_expired(self, retention_days: int = 365) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
        removed = 0
        for record_id, record in self._snapshot_ids():
            created = self._parse_time(record.created_at)
            if created is not None and created < cutoff:
                if self._store.delete(record_id):
                    removed += 1
        return removed

    def prune_low_importance(self, threshold: float = 0.2, keep: int = 100) -> int:
        records = sorted(self._snapshot(), key=lambda r: (r.importance, r.access_count))
        if len(records) <= keep:
            return 0
        removed = 0
        for record in records[:-keep]:
            if record.importance < threshold:
                for record_id, candidate in self._snapshot_ids():
                    if candidate is record:
                        if self._store.delete(record_id):
                            removed += 1
                        break
        return removed

    def prune_to_capacity(self, capacity: int) -> int:
        records = sorted(self._snapshot(), key=lambda r: (r.importance, r.access_count), reverse=True)
        removed = 0
        while len(self._snapshot()) > capacity and records:
            lowest = records.pop()
            for record_id, candidate in self._snapshot_ids():
                if candidate is lowest:
                    if self._store.delete(record_id):
                        removed += 1
                    break
        return removed

    def _snapshot(self) -> list[MemoryRecord]:
        return self._store.list()

    def _snapshot_ids(self) -> list[tuple[str, MemoryRecord]]:
        records = list(self._store.list())
        finder = getattr(self._store, "find_id", None)
        pairs: list[tuple[str, MemoryRecord]] = []
        for record in records:
            record_id = finder(record) if finder else f"mem-{id(record)}"
            pairs.append((record_id, record))
        return pairs

    @staticmethod
    def _parse_time(value: str) -> datetime | None:
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
