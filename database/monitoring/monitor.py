from __future__ import annotations

import time
from typing import Any

from ..database_interfaces import IDatabaseHealthChecker, IDatabaseMetricsCollector
from ..database_models import DatabaseType, QueryProfile


class DatabaseMetricsCollector(IDatabaseMetricsCollector):
    """Collects and stores database metrics in memory."""

    def __init__(self) -> None:
        self._queries: list[QueryProfile] = []
        self._connections: dict[str, int] = {}
        self._pool_stats: dict[str, dict[str, int]] = {}

    def record_query(self, duration_ms: float, driver: str, success: bool) -> None:
        self._queries.append(QueryProfile(
            query="",
            duration_ms=duration_ms,
            rows_affected=0,
            driver=driver,
            success=success,
        ))
        if len(self._queries) > 10_000:
            self._queries = self._queries[-5_000:]

    def record_connection(self, driver: str) -> None:
        self._connections[driver] = self._connections.get(driver, 0) + 1

    def record_disconnection(self, driver: str) -> None:
        self._connections[driver] = max(0, self._connections.get(driver, 0) - 1)

    def record_pool_stats(self, driver: str, active: int, idle: int, waiting: int) -> None:
        self._pool_stats[driver] = {
            "active": active, "idle": idle, "waiting": waiting,
            "total": active + idle + waiting,
        }

    def get_metrics(self) -> dict[str, Any]:
        total = len(self._queries)
        errors = sum(1 for q in self._queries if not q.success)
        avg_ms = sum(q.duration_ms for q in self._queries) / total if total else 0.0
        return {
            "total_queries": total,
            "error_count": errors,
            "avg_duration_ms": round(avg_ms, 2),
            "connections": dict(self._connections),
            "pool_stats": dict(self._pool_stats),
        }

    def reset(self) -> None:
        self._queries.clear()
        self._connections.clear()
        self._pool_stats.clear()


class DatabaseHealthChecker(IDatabaseHealthChecker):
    """Periodic health checker for database drivers."""

    def __init__(self) -> None:
        self._drivers: dict[str, Any] = {}

    def register_driver(self, name: str, driver: Any) -> None:
        self._drivers[name] = driver

    async def check(self) -> dict[str, Any]:
        results: dict[str, Any] = {"status": "healthy", "drivers": {}}
        all_healthy = True
        for name, driver in self._drivers.items():
            driver_result = await self.check_driver(name)
            results["drivers"][name] = driver_result
            if not driver_result.get("healthy", False):
                all_healthy = False
        if not all_healthy:
            results["status"] = "degraded"
        return results

    async def check_driver(self, name: str) -> dict[str, Any]:
        driver = self._drivers.get(name)
        if driver is None:
            return {"name": name, "healthy": False, "error": "Driver not found"}
        try:
            start = time.monotonic()
            ok = await driver.ping()
            latency = round((time.monotonic() - start) * 1000, 2)
            return {
                "name": name,
                "healthy": ok,
                "connected": driver.is_connected,
                "latency_ms": latency,
                "dialect": driver.dialect,
            }
        except Exception as exc:
            return {
                "name": name,
                "healthy": False,
                "connected": False,
                "error": str(exc),
            }


__all__ = [
    "DatabaseMetricsCollector",
    "DatabaseHealthChecker",
]
