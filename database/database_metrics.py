from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from .database_logger import DatabaseLogger
from .database_models import QueryProfile


class DatabaseMetricsCollector:
    """Collects metrics for database operations — latency, throughput, errors, pool stats."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._queries: list[QueryProfile] = []
        self._query_count: int = 0
        self._error_count: int = 0
        self._total_duration_ms: float = 0.0
        self._max_duration_ms: float = 0.0
        self._slow_query_count: int = 0
        self._slow_threshold_ms: float = 1000.0
        self._driver_stats: dict[str, dict[str, float | int]] = defaultdict(
            lambda: {"queries": 0, "errors": 0, "total_ms": 0.0}
        )
        self._pool_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {"active": 0, "idle": 0, "waiting": 0, "total": 0}
        )
        self._connection_count: int = 0
        self._disconnection_count: int = 0
        self._start_time: float = time.time()
        self._logger = logger or DatabaseLogger("database.metrics")

    def record_query(self, duration_ms: float, driver: str = "", success: bool = True) -> None:
        self._query_count += 1
        self._total_duration_ms += duration_ms
        self._max_duration_ms = max(self._max_duration_ms, duration_ms)
        self._driver_stats[driver]["queries"] += 1  # type: ignore[operator]
        self._driver_stats[driver]["total_ms"] += duration_ms  # type: ignore[operator]

        if not success:
            self._error_count += 1
            self._driver_stats[driver]["errors"] += 1  # type: ignore[operator]

        if duration_ms >= self._slow_threshold_ms:
            self._slow_query_count += 1

    def record_connection(self, driver: str = "") -> None:
        self._connection_count += 1

    def record_disconnection(self, driver: str = "") -> None:
        self._disconnection_count += 1

    def record_pool_stats(self, driver: str = "", active: int = 0, idle: int = 0, waiting: int = 0) -> None:
        stats = self._pool_stats[driver]
        stats["active"] = active
        stats["idle"] = idle
        stats["waiting"] = waiting
        stats["total"] = active + idle + waiting

    def get_metrics(self) -> dict[str, Any]:
        uptime = time.time() - self._start_time
        avg_ms = self._total_duration_ms / max(self._query_count, 1)
        return {
            "uptime_seconds": round(uptime, 2),
            "queries": {
                "total": self._query_count,
                "errors": self._error_count,
                "slow": self._slow_query_count,
                "avg_duration_ms": round(avg_ms, 2),
                "max_duration_ms": round(self._max_duration_ms, 2),
                "total_duration_ms": round(self._total_duration_ms, 2),
            },
            "connections": {
                "created": self._connection_count,
                "closed": self._disconnection_count,
                "active": self._connection_count - self._disconnection_count,
            },
            "drivers": dict(self._driver_stats),
            "pools": dict(self._pool_stats),
        }

    def get_driver_metrics(self, driver: str) -> dict[str, Any]:
        stats = self._driver_stats.get(driver, {})
        return {
            "queries": stats.get("queries", 0),
            "errors": stats.get("errors", 0),
            "total_ms": stats.get("total_ms", 0.0),
        }

    def reset(self) -> None:
        self._queries.clear()
        self._query_count = 0
        self._error_count = 0
        self._total_duration_ms = 0.0
        self._max_duration_ms = 0.0
        self._slow_query_count = 0
        self._driver_stats.clear()
        self._pool_stats.clear()
        self._connection_count = 0
        self._disconnection_count = 0
        self._start_time = time.time()

    def set_slow_threshold(self, ms: float) -> None:
        self._slow_threshold_ms = ms
