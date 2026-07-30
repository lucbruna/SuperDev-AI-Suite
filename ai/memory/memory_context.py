from __future__ import annotations

from typing import Any, Dict, List, Optional

from .memory_models import MemoryEntry
from .memory_types import MemoryData, MemoryID, MemoryScope, Tags, Timestamp


class MemoryContext:
    """Builder and manager for memory context around conversations and agents."""

    def __init__(self, context_id: str, max_length: int = 100):
        self._context_id = context_id
        self._max_length = max_length
        self._entries: List[MemoryEntry] = []
        self._metadata: Dict[str, Any] = {}

    @property
    def context_id(self) -> str:
        return self._context_id

    @property
    def max_length(self) -> int:
        return self._max_length

    @property
    def entries(self) -> List[MemoryEntry]:
        return list(self._entries)

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def length(self) -> int:
        return len(self._entries)

    def add_entry(self, entry: MemoryEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > self._max_length:
            self._entries.pop(0)

    def add_data(self, key: MemoryID, data: MemoryData, tags: Tags | None = None) -> MemoryEntry:
        entry = MemoryEntry(key=key, data=data, tags=tags, scope=MemoryScope.SESSION)
        self.add_entry(entry)
        return entry

    def get_entry(self, key: MemoryID) -> MemoryEntry | None:
        for entry in reversed(self._entries):
            if entry.key == key:
                entry.touch()
                return entry
        return None

    def get_recent(self, count: int = 10) -> List[MemoryEntry]:
        return list(self._entries[-count:])

    def search(self, query: str) -> List[MemoryEntry]:
        query_lower = query.lower()
        results: List[MemoryEntry] = []
        for entry in self._entries:
            if query_lower in entry.key.lower():
                results.append(entry)
                continue
            for value in entry.data.values():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(entry)
                    break
        return results

    def filter_by_tags(self, tags: Tags) -> List[MemoryEntry]:
        return [e for e in self._entries if any(t in e.tags for t in tags)]

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def clear(self) -> None:
        self._entries.clear()
        self._metadata.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_id": self._context_id,
            "max_length": self._max_length,
            "entry_count": len(self._entries),
            "metadata": dict(self._metadata),
        }
