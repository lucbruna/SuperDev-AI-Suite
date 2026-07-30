from __future__ import annotations

from typing import Any

from .database_config import DatabaseConfigManager
from .database_engine import DatabaseEngine
from .database_events import DatabaseEventBus
from .database_factory import DatabaseFactory
from .database_health import DatabaseHealthChecker
from .database_interfaces import (
    ICacheEngine,
    IDatabaseDriver,
    IDatabaseEngine,
    IDatabaseHealthChecker,
    IDatabaseMetricsCollector,
    IMigrationEngine,
    IRepository,
    ITransactionManager,
)
from .database_logger import DatabaseLogger
from .database_metrics import DatabaseMetricsCollector
from .database_models import ConnectionConfig, DatabaseConfig
from .database_registry import DatabaseRegistry
from .database_runtime import DatabaseRuntime
from .database_security import DatabaseSecurity


class DatabaseManager:
    """Composition root wiring all database subsystems together."""

    def __init__(self, config: DatabaseConfig | dict[str, Any] | None = None) -> None:
        self._logger = DatabaseLogger("database.manager")
        self._security = DatabaseSecurity(self._logger)
        self._config_mgr = DatabaseConfigManager(self._logger)
        self._registry = DatabaseRegistry(self._logger)
        self._events = DatabaseEventBus(self._logger)
        self._metrics = DatabaseMetricsCollector(self._logger)
        self._factory = DatabaseFactory(self._logger)

        if isinstance(config, dict):
            self._config_mgr.load_from_dict(config)
        elif isinstance(config, DatabaseConfig):
            self._config_mgr = DatabaseConfigManager(self._logger)
        elif config is None:
            self._config_mgr.load_from_env()

        self._engine = DatabaseEngine(
            registry=self._registry,
            config=self._config_mgr,
            event_bus=self._events,
            metrics=self._metrics,
            logger=self._logger,
        )
        self._runtime = DatabaseRuntime(self._engine, self._registry, self._logger)
        self._health = DatabaseHealthChecker(self._registry, self._logger)

    @property
    def engine(self) -> DatabaseEngine:
        return self._engine

    @property
    def registry(self) -> DatabaseRegistry:
        return self._registry

    @property
    def runtime(self) -> DatabaseRuntime:
        return self._runtime

    @property
    def events(self) -> DatabaseEventBus:
        return self._events

    @property
    def metrics(self) -> DatabaseMetricsCollector:
        return self._metrics

    @property
    def health(self) -> DatabaseHealthChecker:
        return self._health

    @property
    def security(self) -> DatabaseSecurity:
        return self._security

    @property
    def logger(self) -> DatabaseLogger:
        return self._logger

    @property
    def factory(self) -> DatabaseFactory:
        return self._factory

    async def start(self) -> None:
        await self._engine.start()
        self._logger.info("Database manager started")

    async def stop(self) -> None:
        await self._engine.stop()
        await self._runtime.close_all()
        self._logger.info("Database manager stopped")

    async def health_check(self) -> dict[str, Any]:
        return await self._health.check_all()

    def get_status(self) -> dict[str, Any]:
        return {
            "running": self._engine.is_running,
            "drivers": self._registry.list_drivers(),
            "repositories": self._registry.list_repositories(),
            "events_subscribers": self._events.handler_count,
            "active_contexts": self._runtime.active_contexts(),
            "metrics": self._metrics.get_metrics(),
        }
