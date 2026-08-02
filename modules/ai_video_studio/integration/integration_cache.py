"""Integration cache — bounded in-memory TTL cache for integration results."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime
from time import monotonic
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float  # monotonic() timestamp


class IntegrationCache:
    """TTL cache with hit/miss stats. Stale entries are evicted on access."""

    def __init__(self, default_ttl: float = 60.0, max_entries: int = 1000) -> None:
        self._default_ttl = default_ttl
        self._max_entries = max_entries
        self._entries: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        entry = self._entries.get(key)
        if entry is None or monotonic() > entry.expires_at:
            if entry is not None:
                self._entries.pop(key, None)
            self._misses += 1
            return None
        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        ttl = self._default_ttl if ttl is None else ttl
        self._entries[key] = CacheEntry(value=value, expires_at=monotonic() + ttl)
        if len(self._entries) > self._max_entries:
            # Drop soonest-to-expire entries until back under the cap.
            for old_key, _ in sorted(
                self._entries.items(), key=lambda kv: kv[1].expires_at
            ):
                if len(self._entries) <= self._max_entries:
                    break
                del self._entries[old_key]

    def delete(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        self._entries.clear()

    def get_or_compute(self, key: str, producer, ttl: float | None = None):  # type: ignore[no-untyped-def]
        """Return cached value or produce + store it (sync producer callable)."""
        value = self.get(key)
        if value is not None:
            return value
        value = producer() if callable(producer) else producer
        self.set(key, value, ttl)
        return value

    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "entries": len(self._entries),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
            "default_ttl_s": self._default_ttl,
            "max_entries": self._max_entries,
            "reported_at": datetime.now(UTC).isoformat(),
        }


_cache: IntegrationCache | None = None


def get_integration_cache() -> IntegrationCache:
    """Process-wide singleton cache."""
    global _cache
    if _cache is None:
        _cache = IntegrationCache()
    return _cache
