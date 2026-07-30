from __future__ import annotations

import time
from typing import Any, Dict, List


class Statistics:
    """Tracks usage and performance statistics for vector memory."""

    def __init__(self):
        self._total_queries: int = 0
        self._total_inserts: int = 0
        self._total_deletes: int = 0
        self._total_updates: int = 0
        self._query_times: List[float] = []
        self._insert_times: List[float] = []
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._start_time: float = time.time()

    @property
    def total_queries(self) -> int:
        return self._total_queries

    @property
    def total_inserts(self) -> int:
        return self._total_inserts

    @property
    def total_deletes(self) -> int:
        return self._total_deletes

    @property
    def total_updates(self) -> int:
        return self._total_updates

    @property
    def cache_hits(self) -> int:
        return self._cache_hits

    @property
    def cache_misses(self) -> int:
        return self._cache_misses

    def record_query(self, duration: float) -> None:
        self._total_queries += 1
        self._query_times.append(duration)

    def record_insert(self, duration: float) -> None:
        self._total_inserts += 1
        self._insert_times.append(duration)

    def record_delete(self) -> None:
        self._total_deletes += 1

    def record_update(self) -> None:
        self._total_updates += 1

    def record_cache_hit(self) -> None:
        self._cache_hits += 1

    def record_cache_miss(self) -> None:
        self._cache_misses += 1

    @property
    def avg_query_time(self) -> float:
        if not self._query_times:
            return 0.0
        return sum(self._query_times) / len(self._query_times)

    @property
    def avg_insert_time(self) -> float:
        if not self._insert_times:
            return 0.0
        return sum(self._insert_times) / len(self._insert_times)

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self._start_time

    @property
    def cache_hit_rate(self) -> float:
        total = self._cache_hits + self._cache_misses
        if total == 0:
            return 0.0
        return self._cache_hits / total

    def snapshot(self) -> Dict[str, Any]:
        return {
            "total_queries": self._total_queries,
            "total_inserts": self._total_inserts,
            "total_deletes": self._total_deletes,
            "total_updates": self._total_updates,
            "avg_query_time": self.avg_query_time,
            "avg_insert_time": self.avg_insert_time,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": self.cache_hit_rate,
            "uptime_seconds": self.uptime_seconds,
        }

    def reset(self) -> None:
        self._total_queries = 0
        self._total_inserts = 0
        self._total_deletes = 0
        self._total_updates = 0
        self._query_times.clear()
        self._insert_times.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._start_time = time.time()
