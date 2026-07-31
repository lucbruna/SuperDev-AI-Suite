"""Short-term memory with FIFO eviction and importance scoring."""
from __future__ import annotations

import time
from typing import Any


class ShortTermMemory:
    """Fixed-size FIFO memory buffer with optional importance-based retention."""

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._store: dict[str, dict[str, Any]] = {}
        self._access_order: list[str] = []

    def store(self, key: str, value: Any) -> None:
        if key in self._store:
            self._access_order.remove(key)
        self._store[key] = {
            "value": value,
            "timestamp": time.time(),
            "access_count": self._store.get(key, {}).get("access_count", 0) + 1,
        }
        self._access_order.append(key)
        self._evict()

    def retrieve(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        entry["access_count"] = entry.get("access_count", 0) + 1
        entry["last_accessed"] = time.time()
        return entry.get("value")

    def remove(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            self._access_order.remove(key)
            return True
        return False

    def contains(self, key: str) -> bool:
        return key in self._store

    def count(self) -> int:
        return len(self._store)

    def get_all(self) -> dict[str, Any]:
        return {k: v.get("value") for k, v in self._store.items()}

    def keys(self) -> list[str]:
        return list(self._access_order)

    def clear(self) -> None:
        self._store.clear()
        self._access_order.clear()

    def _evict(self) -> None:
        while len(self._store) > self._max_size:
            oldest = self._access_order.pop(0)
            self._store.pop(oldest, None)

    def snapshot(self) -> dict[str, Any]:
        return {
            "size": len(self._store),
            "max_size": self._max_size,
            "keys": list(self._access_order),
        }
