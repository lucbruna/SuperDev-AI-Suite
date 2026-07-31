from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

from ..knowledge_interfaces import MemoryStore
from ..knowledge_models import MemoryRecord


class InMemoryMemoryStorage(MemoryStore):
    """Thread-safe in-memory persistence for memory records."""

    def __init__(self, limit: int = 10000) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.storage")
        self._records: dict[str, MemoryRecord] = {}
        self._limit = limit
        self._lock = threading.RLock()
        self._next_id = 1

    def save(self, record: MemoryRecord) -> str:
        with self._lock:
            record_id = f"mem-{self._next_id}"
            self._next_id += 1
            self._records[record_id] = record
            self._enforce_limit()
            return record_id

    def get(self, record_id: str) -> MemoryRecord | None:
        with self._lock:
            record = self._records.get(record_id)
            if record is not None:
                record.access_count += 1
            return record

    def list(self, memory_type: str | None = None) -> list[MemoryRecord]:
        with self._lock:
            records = list(self._records.values())
        if memory_type:
            records = [r for r in records if r.memory_type == memory_type]
        return records

    def delete(self, record_id: str) -> bool:
        with self._lock:
            return self._records.pop(record_id, None) is not None

    def find_id(self, record: MemoryRecord) -> str | None:
        """Resolve the store ID for a record object by identity."""
        with self._lock:
            for record_id, candidate in self._records.items():
                if candidate is record:
                    return record_id
        return None

    def clear(self) -> None:
        with self._lock:
            self._records.clear()

    def count(self) -> int:
        with self._lock:
            return len(self._records)

    def _enforce_limit(self) -> None:
        while len(self._records) > self._limit:
            oldest = min(self._records, key=lambda rid: self._records[rid].created_at)
            self._records.pop(oldest, None)

    def to_dict(self) -> dict[str, Any]:
        with self._lock:
            return {rid: rec.to_dict() for rid, rec in self._records.items()}

    def load_dict(self, data: dict[str, dict[str, Any]]) -> None:
        with self._lock:
            self._records = {
                rid: MemoryRecord(**{k: v for k, v in item.items() if k in MemoryRecord.__dataclass_fields__})
                for rid, item in data.items()
            }


class FileMemoryStorage(MemoryStore):
    """JSON-file-backed memory persistence."""

    def __init__(self, path: str | Path = ".knowledge/memory.json") -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.file")
        self._path = Path(path)
        self._inner = InMemoryMemoryStorage()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def save(self, record: MemoryRecord) -> str:
        record_id = self._inner.save(record)
        self._persist()
        return record_id

    def get(self, record_id: str) -> MemoryRecord | None:
        return self._inner.get(record_id)

    def list(self, memory_type: str | None = None) -> list[MemoryRecord]:
        return self._inner.list(memory_type)

    def delete(self, record_id: str) -> bool:
        deleted = self._inner.delete(record_id)
        if deleted:
            self._persist()
        return deleted

    def find_id(self, record: MemoryRecord) -> str | None:
        return self._inner.find_id(record)

    def clear(self) -> None:
        self._inner.clear()
        self._persist()

    def count(self) -> int:
        return self._inner.count()

    def _persist(self) -> None:
        try:
            self._path.write_text(json.dumps(self._inner.to_dict()), encoding="utf-8")
        except OSError as exc:  # noqa: BLE001
            self._log.warning("failed to persist memory: %s", exc)

    def _load(self) -> None:
        try:
            if self._path.exists():
                data = json.loads(self._path.read_text(encoding="utf-8"))
                self._inner.load_dict(data)
        except (OSError, json.JSONDecodeError) as exc:  # noqa: BLE001
            self._log.warning("failed to load memory: %s", exc)
