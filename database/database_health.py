from __future__ import annotations

import time
from typing import Any

from .database_logger import DatabaseLogger
from .database_registry import DatabaseRegistry


class DatabaseHealthChecker:
    """Health checks for database connections."""

    def __init__(self, registry: DatabaseRegistry, logger: DatabaseLogger | None = None) -> None:
        self._registry = registry
        self._logger = logger or DatabaseLogger("database.health")

    async def check_all(self) -> dict[str, Any]:
        statuses: dict[str, Any] = {}
        overall = True
        for name in self._registry.list_drivers():
            try:
                status = await self.check_driver(name)
                statuses[name] = status
                if not status.get("healthy", False):
                    overall = False
            except Exception as exc:
                statuses[name] = {"healthy": False, "error": str(exc)}
                overall = False

        return {"healthy": overall, "drivers": statuses, "timestamp": time.time()}

    async def check_driver(self, name: str) -> dict[str, Any]:
        try:
            driver = self._registry.get_driver(name)
            start = time.monotonic()
            ping_ok = await driver.ping()
            elapsed = time.monotonic() - start

            return {
                "healthy": ping_ok,
                "driver": name,
                "dialect": driver.dialect,
                "connected": driver.is_connected,
                "ping_ms": round(elapsed * 1000, 2),
                "timestamp": time.time(),
            }
        except KeyError:
            return {"healthy": False, "driver": name, "error": "Driver not registered"}
        except Exception as exc:
            return {"healthy": False, "driver": name, "error": str(exc)}

    async def ping(self, driver_name: str) -> bool:
        try:
            driver = self._registry.get_driver(driver_name)
            return await driver.ping()
        except Exception:
            return False

    def summary(self) -> dict[str, Any]:
        drivers = self._registry.list_drivers()
        return {
            "total_drivers": len(drivers),
            "drivers": drivers,
            "healthy": True,
        }
