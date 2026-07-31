"""Cache Manager - Intelligent offline caching."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CacheEntry:
    key: str
    data: Any = None
    size_bytes: int = 0
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    access_count: int = 0


class CacheManager:
    def __init__(self, max_size_bytes: int = 500 * 1024 * 1024):
        self.entries: dict[str, CacheEntry] = {}
        self.max_size_bytes = max_size_bytes
        self.current_size: int = 0

    def put(self, key: str, data: Any, size_bytes: int = 1024, priority: int = 0, ttl_seconds: int = 3600) -> bool:
        if self.current_size + size_bytes > self.max_size_bytes:
            self._evict()
        entry = CacheEntry(key=key, data=data, size_bytes=size_bytes, priority=priority)
        self.entries[key] = entry
        self.current_size += size_bytes
        return True

    def get(self, key: str) -> Any | None:
        entry = self.entries.get(key)
        if entry:
            entry.access_count += 1
            return entry.data
        return None

    def remove(self, key: str) -> bool:
        entry = self.entries.pop(key, None)
        if entry:
            self.current_size -= entry.size_bytes
            return True
        return False

    def contains(self, key: str) -> bool:
        return key in self.entries

    def clear(self) -> int:
        count = len(self.entries)
        self.entries.clear()
        self.current_size = 0
        return count

    def size(self) -> int:
        return len(self.entries)

    def _evict(self) -> None:
        if not self.entries:
            return
        min_key = min(self.entries, key=lambda k: (self.entries[k].priority, self.entries[k].access_count))
        self.remove(min_key)

    def list_keys(self) -> list[str]:
        return list(self.entries.keys())
