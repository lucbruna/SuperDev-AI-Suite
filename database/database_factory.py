from __future__ import annotations

from typing import Any

from .database_config import DatabaseConfigManager
from .database_engine import DatabaseEngine
from .database_events import DatabaseEventBus
from .database_interfaces import IDatabaseDriver, IDatabaseEngine
from .database_logger import DatabaseLogger
from .database_metrics import DatabaseMetricsCollector
from .database_models import DatabaseConfig
from .database_registry import DatabaseRegistry


class DatabaseFactory:
    """Factory for creating engine, driver, and registry instances from config."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._logger = logger or DatabaseLogger("database.factory")

    def create_engine(
        self,
        config: DatabaseConfig | dict[str, Any] | None = None,
        registry: DatabaseRegistry | None = None,
    ) -> DatabaseEngine:
        config_mgr = DatabaseConfigManager(self._logger)

        if isinstance(config, dict):
            config_mgr.load_from_dict(config)
        elif isinstance(config, DatabaseConfig):
            config_mgr = DatabaseConfigManager(self._logger)
        else:
            config_mgr.load_from_env()

        event_bus = DatabaseEventBus(self._logger)
        metrics = DatabaseMetricsCollector(self._logger)
        reg = registry or DatabaseRegistry(self._logger)

        engine = DatabaseEngine(
            registry=reg,
            config=config_mgr,
            event_bus=event_bus,
            metrics=metrics,
            logger=self._logger,
        )

        return engine

    def create_engine_from_json(self, path: str) -> DatabaseEngine:
        config_mgr = DatabaseConfigManager(self._logger)
        config_mgr.load_from_json(path)
        config = config_mgr.get_config()

        registry = DatabaseRegistry(self._logger)
        event_bus = DatabaseEventBus(self._logger)
        metrics = DatabaseMetricsCollector(self._logger)

        return DatabaseEngine(
            registry=registry,
            config=config_mgr,
            event_bus=event_bus,
            metrics=metrics,
            logger=self._logger,
        )

    def register_driver(self, engine: IDatabaseEngine, name: str, driver: IDatabaseDriver) -> None:
        engine.register_driver(name, driver)
        self._logger.info(f"Driver '{name}' registered via factory")

    def new_registry(self) -> DatabaseRegistry:
        return DatabaseRegistry(self._logger)
