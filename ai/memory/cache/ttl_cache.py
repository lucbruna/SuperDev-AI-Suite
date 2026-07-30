from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .cache_entry import CacheEntry


class TTLCache:
    """Time-To-Live based cache."""

    def __init__(self, default_ttl: float = 60.0, max_size: int = 1000) -> None:
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._entries: Dict[str, CacheEntry] = {}

    @property
    def default_ttl(self) -> float:
        return self._default_ttl

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def size(self) -> int:
        self._purge_expired()
        return len(self._entries)

    def get(self, key: str) -> Optional[Any]:
        entry = self._entries.get(key)
        if entry is None or entry.is_expired:
            if entry:
                del self._entries[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        self._purge_expired()
        if len(self._entries) >= self._max_size:
            self._evict()
        actual_ttl = ttl if ttl is not None else self._default_ttl
        self._entries[key] = CacheEntry(key, value, actual_ttl)

    def delete(self, key: str) -> bool:
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def clear(self) -> None:
        self._entries.clear()

    def remaining_ttl(self, key: str) -> Optional[float]:
        entry = self._entries.get(key)
        if entry is None:
            return None
        remaining = entry.ttl - (time.time() - entry.created_at)
        return max(remaining, 0.0)

    def keys(self) -> List[str]:
        self._purge_expired()
        return list(self._entries.keys())

    def _purge_expired(self) -> None:
        expired = [k for k, e in self._entries.items() if e.is_expired]
        for k in expired:
            del self._entries[k]

    def _evict(self) -> None:
        if self._entries:
            oldest = min(self._entries.keys(), key=lambda k: self._entries[k].created_at)
            del self._entries[oldest]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_ttl": self._default_ttl,
            "max_size": self._max_size,
            "size": self.size,
        }
