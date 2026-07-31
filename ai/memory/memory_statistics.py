from __future__ import annotations

import time
from collections import Counter
from typing import Any

from .memory_models import MemoryEntry


class MemoryStatistics:
    """Statistics tracking for memory usage patterns and growth."""

    def __init__(self):
        self._scope_distribution: Counter[str] = Counter()
        self._category_distribution: Counter[str] = Counter()
        self._status_distribution: Counter[str] = Counter()
        self._tag_frequency: Counter[str] = Counter()
        self._access_frequency: dict[str, int] = {}
        self._size_history: list[dict[str, Any]] = []
        self._growth_rate: float = 0.0
        self._peak_size: int = 0
        self._last_update: float = time.time()

    def record_entry(self, entry: MemoryEntry) -> None:
        self._scope_distribution[entry.scope.name] += 1
        self._category_distribution[entry.category.name] += 1
        self._status_distribution[entry.status.name] += 1
        for tag in entry.tags:
            self._tag_frequency[tag] += 1
        self._access_frequency[entry.key] = entry.access_count

    def record_access(self, key: str) -> None:
        self._access_frequency[key] = self._access_frequency.get(key, 0) + 1

    def update_size(self, total_entries: int, total_size: int) -> None:
        now = time.time()
        self._size_history.append({
            "timestamp": now,
            "entries": total_entries,
            "size_bytes": total_size,
        })
        if total_size > self._peak_size:
            self._peak_size = total_size
        if len(self._size_history) >= 2:
            prev = self._size_history[-2]
            time_delta = now - prev["timestamp"]
            if time_delta > 0:
                self._growth_rate = (total_entries - prev["entries"]) / time_delta
        if len(self._size_history) > 1000:
            self._size_history = self._size_history[-500:]
        self._last_update = now

    @property
    def scope_distribution(self) -> dict[str, int]:
        return dict(self._scope_distribution)

    @property
    def category_distribution(self) -> dict[str, int]:
        return dict(self._category_distribution)

    @property
    def status_distribution(self) -> dict[str, int]:
        return dict(self._status_distribution)

    @property
    def tag_frequency(self) -> dict[str, int]:
        return dict(self._tag_frequency)

    @property
    def growth_rate(self) -> float:
        return self._growth_rate

    @property
    def peak_size(self) -> int:
        return self._peak_size

    @property
    def top_tags(self, n: int = 10) -> list[tuple[str, int]]:
        return self._tag_frequency.most_common(n)

    @property
    def most_accessed(self, n: int = 10) -> list[tuple[str, int]]:
        sorted_keys = sorted(
            self._access_frequency.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_keys[:n]

    def snapshot(self) -> dict[str, Any]:
        return {
            "scope_distribution": dict(self._scope_distribution),
            "category_distribution": dict(self._category_distribution),
            "status_distribution": dict(self._status_distribution),
            "tag_count": len(self._tag_frequency),
            "growth_rate": self._growth_rate,
            "peak_size": self._peak_size,
            "unique_keys": len(self._access_frequency),
            "last_update": self._last_update,
        }

    def clear(self) -> None:
        self._scope_distribution.clear()
        self._category_distribution.clear()
        self._status_distribution.clear()
        self._tag_frequency.clear()
        self._access_frequency.clear()
        self._size_history.clear()
        self._growth_rate = 0.0
        self._peak_size = 0
