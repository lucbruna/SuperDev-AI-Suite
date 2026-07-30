from __future__ import annotations

from typing import Any, Dict, List


class CachePolicy:
    """Defines eviction and expiration policies."""

    EVICT_LRU = "lru"
    EVICT_LFU = "lfu"
    EVICT_FIFO = "fifo"

    def __init__(self, eviction_strategy: str = EVICT_LRU, max_size: int = 1000) -> None:
        self._eviction_strategy = eviction_strategy
        self._max_size = max_size

    @property
    def eviction_strategy(self) -> str:
        return self._eviction_strategy

    @property
    def max_size(self) -> int:
        return self._max_size

    def should_evict(self, current_size: int) -> bool:
        return current_size >= self._max_size

    def select_victim(self, entries: List[Dict[str, Any]]) -> str:
        if self._eviction_strategy == self.EVICT_LRU:
            return min(entries, key=lambda e: e["accessed_at"])["key"]
        if self._eviction_strategy == self.EVICT_LFU:
            return min(entries, key=lambda e: e["access_count"])["key"]
        return min(entries, key=lambda e: e["created_at"])["key"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eviction_strategy": self._eviction_strategy,
            "max_size": self._max_size,
        }
