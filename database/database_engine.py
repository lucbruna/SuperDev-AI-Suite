from __future__ import annotations

from typing import Any

from .database_config import DatabaseConfigManager
from .database_context import DatabaseContext
from .database_events import DatabaseEventBus, DatabaseEventType
from .database_interfaces import IDatabaseDriver, IDatabaseEngine
from .database_logger import DatabaseLogger
from .database_metrics import DatabaseMetricsCollector
from .database_models import DatabaseConfig, QueryResult
from .database_registry import DatabaseRegistry


class DatabaseEngine(IDatabaseEngine):
    """Central engine orchestrating drivers, execution, events, and lifecycle."""

    def __init__(
        self,
        registry: DatabaseRegistry | None = None,
        config: DatabaseConfigManager | None = None,
        event_bus: DatabaseEventBus | None = None,
        metrics: DatabaseMetricsCollector | None = None,
        logger: DatabaseLogger | None = None,
    ) -> None:
        self._registry = registry or DatabaseRegistry()
        self._config_mgr = config or DatabaseConfigManager()
        self._config = self._config_mgr.get_config()
        self._events = event_bus or DatabaseEventBus()
        self._metrics = metrics or DatabaseMetricsCollector()
        self._logger = logger or DatabaseLogger("database.engine")
        self._running = False

    async def start(self) -> None:
        self._running = True
        for name in list(self._registry.list_drivers()):
            try:
                driver = self._registry.get_driver(name)
                conn_cfg = self._registry.get_connection(name)
                if conn_cfg:
                    await driver.connect(conn_cfg)
                    await self._events.emit(DatabaseEventType.CONNECT, {"driver": name})
                    self._metrics.record_connection(name)
                    self._logger.info(f"Started driver: {name}")
            except Exception as exc:
                self._logger.error(f"Failed to start driver '{name}': {exc}")
        self._logger.info("Database engine started")

    async def stop(self) -> None:
        self._running = False
        for name in list(self._registry.list_drivers()):
            try:
                driver = self._registry.get_driver(name)
                if driver.is_connected:
                    await driver.disconnect()
                    await self._events.emit(DatabaseEventType.DISCONNECT, {"driver": name})
                    self._metrics.record_disconnection(name)
            except Exception as exc:
                self._logger.error(f"Failed to stop driver '{name}': {exc}")
        self._logger.info("Database engine stopped")

    def get_driver(self, name: str) -> IDatabaseDriver:
        return self._registry.get_driver(name)

    def register_driver(self, name: str, driver: IDatabaseDriver) -> None:
        self._registry.register_driver(name, driver)

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        import time

        driver_name = self._config.default_driver
        driver = self._registry.get_driver(driver_name)
        start = time.monotonic()
        try:
            result = await driver.execute(query, params)
            elapsed = (time.monotonic() - start) * 1000
            self._metrics.record_query(elapsed, driver_name, True)
            await self._events.emit(DatabaseEventType.QUERY_EXECUTED, {"query": query[:100], "duration_ms": elapsed})
            if self._config.log_queries:
                self._logger.query(query, elapsed)
            if elapsed >= self._config.slow_query_threshold_ms:
                self._logger.slow_query(query, elapsed, self._config.slow_query_threshold_ms)
                await self._events.emit(DatabaseEventType.QUERY_SLOW, {"query": query[:100], "duration_ms": elapsed})
            return result
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            self._metrics.record_query(elapsed, driver_name, False)
            await self._events.emit(DatabaseEventType.QUERY_ERROR, {"query": query[:100], "error": str(exc)})
            self._logger.error(f"Query failed ({elapsed:.2f}ms): {exc}")
            return QueryResult(error=str(exc))

    async def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        result = await self.execute(query, params)
        return result.rows

    async def health_check(self) -> dict[str, Any]:
        from .database_health import DatabaseHealthChecker

        checker = DatabaseHealthChecker(self._registry)
        return await checker.check_all()

    @property
    def config(self) -> DatabaseConfig:
        return self._config

    @property
    def registry(self) -> DatabaseRegistry:
        return self._registry

    @property
    def event_bus(self) -> DatabaseEventBus:
        return self._events

    @property
    def metrics(self) -> DatabaseMetricsCollector:
        return self._metrics

    @property
    def logger(self) -> DatabaseLogger:
        return self._logger

    @property
    def is_running(self) -> bool:
        return self._running
