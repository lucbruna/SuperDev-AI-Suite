from __future__ import annotations

import time
from typing import Any


class MemoryMetrics:
    """Metrics collection for the memory subsystem."""

    def __init__(self):
        self._store_count: int = 0
        self._retrieve_count: int = 0
        self._update_count: int = 0
        self._delete_count: int = 0
        self._hit_count: int = 0
        self._miss_count: int = 0
        self._eviction_count: int = 0
        self._error_count: int = 0
        self._total_latency: float = 0.0
        self._operation_count: int = 0
        self._latency_buckets: dict[str, list[float]] = {}
        self._start_time: float = time.time()

    @property
    def store_count(self) -> int:
        return self._store_count

    @property
    def retrieve_count(self) -> int:
        return self._retrieve_count

    @property
    def update_count(self) -> int:
        return self._update_count

    @property
    def delete_count(self) -> int:
        return self._delete_count

    @property
    def hit_count(self) -> int:
        return self._hit_count

    @property
    def miss_count(self) -> int:
        return self._miss_count

    @property
    def eviction_count(self) -> int:
        return self._eviction_count

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def hit_rate(self) -> float:
        total = self._hit_count + self._miss_count
        return self._hit_count / total if total > 0 else 0.0

    @property
    def avg_latency(self) -> float:
        return self._total_latency / self._operation_count if self._operation_count > 0 else 0.0

    @property
    def uptime(self) -> float:
        return time.time() - self._start_time

    def record_store(self, latency: float = 0.0) -> None:
        self._store_count += 1
        self._record_latency("store", latency)

    def record_retrieve(self, hit: bool, latency: float = 0.0) -> None:
        self._retrieve_count += 1
        if hit:
            self._hit_count += 1
        else:
            self._miss_count += 1
        self._record_latency("retrieve", latency)

    def record_update(self, latency: float = 0.0) -> None:
        self._update_count += 1
        self._record_latency("update", latency)

    def record_delete(self, latency: float = 0.0) -> None:
        self._delete_count += 1
        self._record_latency("delete", latency)

    def record_eviction(self) -> None:
        self._eviction_count += 1

    def record_error(self) -> None:
        self._error_count += 1

    def _record_latency(self, operation: str, latency: float) -> None:
        self._total_latency += latency
        self._operation_count += 1
        if operation not in self._latency_buckets:
            self._latency_buckets[operation] = []
        self._latency_buckets[operation].append(latency)
        if len(self._latency_buckets[operation]) > 1000:
            self._latency_buckets[operation] = self._latency_buckets[operation][-500:]

    def get_latency_stats(self, operation: str) -> dict[str, float]:
        buckets = self._latency_buckets.get(operation, [])
        if not buckets:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        return {
            "avg": sum(buckets) / len(buckets),
            "min": min(buckets),
            "max": max(buckets),
            "count": len(buckets),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "store_count": self._store_count,
            "retrieve_count": self._retrieve_count,
            "update_count": self._update_count,
            "delete_count": self._delete_count,
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "eviction_count": self._eviction_count,
            "error_count": self._error_count,
            "hit_rate": self.hit_rate,
            "avg_latency": self.avg_latency,
            "uptime": self.uptime,
        }

    def reset(self) -> None:
        self.__init__()
