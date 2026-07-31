from __future__ import annotations

import logging
import time
from typing import Any


class GatewayCache:
    """Simple TTL cache for gateway responses."""

    def __init__(self, ttl: float = 60.0, max_entries: int = 1000) -> None:
        self._log = logging.getLogger("superdev.integration.gateway.caching")
        self.ttl = ttl
        self.max_entries = max_entries
        self._cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        stored_at, value = entry
        if time.monotonic() - stored_at > self.ttl:
            self._cache.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._cache) >= self.max_entries and key not in self._cache:
            oldest = min(self._cache, key=lambda k: self._cache[k][0])
            self._cache.pop(oldest, None)
        self._cache[key] = (time.monotonic(), value)

    def invalidate(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)
