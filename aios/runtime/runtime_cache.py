"""AIOS Runtime Cache — TTL cache shared by runtimes.

Deterministic TTL cache used to memoize results across runtime kinds.
"""

from __future__ import annotations

import threading
import time
from typing import Any


class RuntimeCache:
    """Thread-safe TTL cache."""

    def __init__(self, default_ttl: float = 60.0, max_entries: int = 1000) -> None:
        self.default_ttl = default_ttl
        self.max_entries = max_entries
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires = time.time() + (self.default_ttl if ttl is None else ttl)
        with self._lock:
            self._store[key] = (expires, value)
            if len(self._store) > self.max_entries:
                oldest = min(self._store, key=lambda k: self._store[k][0])
                del self._store[oldest]

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return default
            expires, value = item
            if expires < time.time():
                del self._store[key]
                return default
            return value

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {"entries": len(self._store), "max_entries": self.max_entries}
