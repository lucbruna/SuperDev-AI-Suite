from __future__ import annotations

import time
from typing import Any


class CacheCollector:
    """Collects cache performance metrics."""

    def __init__(self) -> None:
        self._hits = 0
        self._misses = 0
        self._size = 0

    def record_hit(self) -> None:
        self._hits += 1

    def record_miss(self) -> None:
        self._misses += 1

    def record_size(self, size: int) -> None:
        self._size = size

    def collect(self) -> dict[str, Any]:
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4),
            "size": self._size,
            "timestamp": time.time(),
        }
