from __future__ import annotations

from typing import Any

from .cache_entry import CacheEntry


class LRUCache:
    """Least Recently Used cache implementation."""

    def __init__(self, max_size: int = 1000) -> None:
        self._max_size = max_size
        self._entries: dict[str, CacheEntry] = {}
        self._order: list[str] = []

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def size(self) -> int:
        return len(self._entries)

    def get(self, key: str) -> Any | None:
        entry = self._entries.get(key)
        if entry is None or entry.is_expired:
            if entry:
                self._remove(key)
            return None
        self._touch(key)
        return entry.value

    def set(self, key: str, value: Any, ttl: float = 300.0) -> None:
        if key in self._entries:
            self._entries[key].value = value
            self._touch(key)
        else:
            if self.size >= self._max_size:
                self._evict()
            self._entries[key] = CacheEntry(key, value, ttl)
            self._order.append(key)

    def delete(self, key: str) -> bool:
        return self._remove(key)

    def clear(self) -> None:
        self._entries.clear()
        self._order.clear()

    def keys(self) -> list[str]:
        return list(self._entries.keys())

    def _touch(self, key: str) -> None:
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def _remove(self, key: str) -> bool:
        if key in self._entries:
            del self._entries[key]
            if key in self._order:
                self._order.remove(key)
            return True
        return False

    def _evict(self) -> None:
        if self._order:
            oldest = self._order.pop(0)
            self._entries.pop(oldest, None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_size": self._max_size,
            "size": self.size,
            "order": list(self._order),
        }
