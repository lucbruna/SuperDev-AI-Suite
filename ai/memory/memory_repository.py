from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .memory_exceptions import MemoryNotFoundError
from .memory_models import MemoryEntry, MemoryQuery
from .memory_types import MemoryData, MemoryID, MemoryScope, MemoryStatus, Tags


class MemoryRepository:
    """Data access layer for memory entries with CRUD and search."""

    def __init__(self, storage_dir: str | Path | None = None):
        self._storage_dir = Path(storage_dir) if storage_dir else None
        self._entries: Dict[str, MemoryEntry] = {}

    @property
    def storage_dir(self) -> Path | None:
        return self._storage_dir

    async def store(self, entry: MemoryEntry) -> None:
        self._entries[entry.key] = entry
        if self._storage_dir:
            await self._write_to_disk(entry)

    async def retrieve(self, key: MemoryID) -> MemoryEntry | None:
        entry = self._entries.get(key)
        if entry is None and self._storage_dir:
            entry = await self._read_from_disk(key)
        if entry:
            entry.touch()
        return entry

    async def retrieve_or_raise(self, key: MemoryID) -> MemoryEntry:
        entry = await self.retrieve(key)
        if entry is None:
            raise MemoryNotFoundError(f"Memory entry not found: {key}")
        return entry

    async def update(self, key: MemoryID, data: MemoryData) -> bool:
        entry = self._entries.get(key)
        if entry is None:
            return False
        entry.data = data
        if self._storage_dir:
            await self._write_to_disk(entry)
        return True

    async def delete(self, key: MemoryID) -> bool:
        if key in self._entries:
            del self._entries[key]
            if self._storage_dir:
                self._delete_from_disk(key)
            return True
        return False

    async def exists(self, key: MemoryID) -> bool:
        return key in self._entries

    async def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        results: List[MemoryEntry] = []
        for entry in self._entries.values():
            if not query.include_expired and entry.is_expired:
                continue
            if query.scope and entry.scope != query.scope:
                continue
            if query.category and entry.category != query.category:
                continue
            if query.status and entry.status != query.status:
                continue
            if query.tags and not any(t in entry.tags for t in query.tags):
                continue
            if entry.priority < query.min_priority:
                continue
            if query.query:
                q = query.query.lower()
                if q not in entry.key.lower():
                    found = False
                    for value in entry.data.values():
                        if isinstance(value, str) and q in value.lower():
                            found = True
                            break
                    if not found:
                        continue
            results.append(entry)
        results.sort(key=lambda e: e.priority, reverse=True)
        return results[:query.max_results]

    async def clear(self, scope: MemoryScope | None = None) -> None:
        if scope is None:
            self._entries.clear()
        else:
            keys = [k for k, e in self._entries.items() if e.scope == scope]
            for k in keys:
                del self._entries[k]

    async def count(self, scope: MemoryScope | None = None) -> int:
        if scope is None:
            return len(self._entries)
        return sum(1 for e in self._entries.values() if e.scope == scope)

    async def list_keys(self) -> List[MemoryID]:
        return list(self._entries.keys())

    async def _write_to_disk(self, entry: MemoryEntry) -> None:
        if not self._storage_dir:
            return
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        path = self._storage_dir / f"{entry.key}.json"
        path.write_text(json.dumps(entry.to_dict(), indent=2))

    async def _read_from_disk(self, key: str) -> MemoryEntry | None:
        if not self._storage_dir:
            return None
        path = self._storage_dir / f"{key}.json"
        if path.exists():
            data = json.loads(path.read_text())
            entry = MemoryEntry.from_dict(data)
            self._entries[key] = entry
            return entry
        return None

    def _delete_from_disk(self, key: str) -> None:
        if not self._storage_dir:
            return
        path = self._storage_dir / f"{key}.json"
        path.unlink(missing_ok=True)
