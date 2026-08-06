"""Knowledge memory — bounded in-memory cache with LRU eviction.

Used for parsed files, intermediate results and hot lookups so repeated
pipeline runs and queries stay fast without unbounded growth.
"""
from __future__ import annotations

import logging
import time
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)


class KnowledgeMemory:
    """A simple LRU cache with byte/entry accounting."""

    def __init__(self, capacity: int = 10_000) -> None:
        self._capacity = max(capacity, 1)
        self._store: OrderedDict[str, tuple[Any, float, int]] = OrderedDict()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def size(self) -> int:
        return len(self._store)

    @property
    def is_empty(self) -> bool:
        return not self._store

    def put(self, key: str, value: Any, size_bytes: int = 0) -> None:
        """Insert or refresh an entry; evict least-recently-used when full."""
        self._store[key] = (value, time.time(), size_bytes)
        self._store.move_to_end(key)
        while len(self._store) > self._capacity:
            self._store.popitem(last=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Return a value and refresh its recency, or ``default``."""
        entry = self._store.get(key)
        if entry is None:
            return default
        value, _stamp, _size = entry
        self._store.move_to_end(key)
        return value

    def contains(self, key: str) -> bool:
        return key in self._store

    def evict(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        self._store.clear()

    def keys(self) -> list[str]:
        return list(self._store)

    def stats(self) -> dict[str, Any]:
        total_bytes = sum(entry[2] for entry in self._store.values())
        return {
            "entries": len(self._store),
            "capacity": self._capacity,
            "bytes": total_bytes,
            "usage_ratio": round(len(self._store) / self._capacity, 3),
        }
