from __future__ import annotations

from typing import Any

from .database_interfaces import (
    ICacheEngine,
    IDatabaseDriver,
    IDatabaseEngine,
    IMigrationEngine,
    IRepository,
    ITransactionManager,
)
from .database_logger import DatabaseLogger
from .database_models import ConnectionConfig


class DatabaseRegistry:
    """Registry for drivers, migrations, repositories, and cache engines."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._drivers: dict[str, IDatabaseDriver] = {}
        self._engines: dict[str, IDatabaseEngine] = {}
        self._repositories: dict[str, IRepository] = {}
        self._migrations: dict[str, IMigrationEngine] = {}
        self._cache: dict[str, ICacheEngine] = {}
        self._transactions: dict[str, ITransactionManager] = {}
        self._connections: dict[str, ConnectionConfig] = {}
        self._driver_aliases: dict[str, str] = {
            "postgres": "postgresql",
            "pg": "postgresql",
            "sqlite3": "sqlite",
            "mysql": "mysql",
            "mariadb": "mariadb",
            "mssql": "sqlserver",
            "elastic": "elasticsearch",
            "neo": "neo4j",
        }
        self._logger = logger or DatabaseLogger("database.registry")

    def register_driver(self, name: str, driver: IDatabaseDriver) -> None:
        self._drivers[name] = driver
        self._logger.info(f"Registered driver: {name}")

    def get_driver(self, name: str) -> IDatabaseDriver:
        resolved = self._driver_aliases.get(name, name)
        driver = self._drivers.get(resolved)
        if driver is None:
            raise KeyError(f"Driver '{name}' not registered (resolved: '{resolved}')")
        return driver

    def unregister_driver(self, name: str) -> bool:
        resolved = self._driver_aliases.get(name, name)
        if resolved in self._drivers:
            del self._drivers[resolved]
            self._logger.info(f"Unregistered driver: {resolved}")
            return True
        return False

    def list_drivers(self) -> list[str]:
        return list(self._drivers.keys())

    def register_engine(self, name: str, engine: IDatabaseEngine) -> None:
        self._engines[name] = engine

    def get_engine(self, name: str) -> IDatabaseEngine:
        engine = self._engines.get(name)
        if engine is None:
            raise KeyError(f"Engine '{name}' not registered")
        return engine

    def register_repository(self, name: str, repo: IRepository) -> None:
        self._repositories[name] = repo

    def get_repository(self, name: str) -> IRepository:
        repo = self._repositories.get(name)
        if repo is None:
            raise KeyError(f"Repository '{name}' not registered")
        return repo

    def list_repositories(self) -> list[str]:
        return list(self._repositories.keys())

    def register_migration(self, name: str, engine: IMigrationEngine) -> None:
        self._migrations[name] = engine

    def get_migration(self, name: str) -> IMigrationEngine:
        migration = self._migrations.get(name)
        if migration is None:
            raise KeyError(f"Migration engine '{name}' not registered")
        return migration

    def register_cache(self, name: str, cache: ICacheEngine) -> None:
        self._cache[name] = cache

    def get_cache(self, name: str = "default") -> ICacheEngine:
        cache = self._cache.get(name)
        if cache is None:
            raise KeyError(f"Cache '{name}' not registered")
        return cache

    def register_transaction(self, name: str, tx: ITransactionManager) -> None:
        self._transactions[name] = tx

    def get_transaction(self, name: str = "default") -> ITransactionManager:
        tx = self._transactions.get(name)
        if tx is None:
            raise KeyError(f"Transaction manager '{name}' not registered")
        return tx

    def register_connection(self, name: str, config: ConnectionConfig) -> None:
        self._connections[name] = config

    def get_connection(self, name: str) -> ConnectionConfig:
        conn = self._connections.get(name)
        if conn is None:
            raise KeyError(f"Connection '{name}' not registered")
        return conn

    def clear(self) -> None:
        self._drivers.clear()
        self._engines.clear()
        self._repositories.clear()
        self._migrations.clear()
        self._cache.clear()
        self._transactions.clear()
        self._connections.clear()

    def status(self) -> dict[str, Any]:
        return {
            "drivers": list(self._drivers.keys()),
            "engines": list(self._engines.keys()),
            "repositories": list(self._repositories.keys()),
            "migrations": list(self._migrations.keys()),
            "caches": list(self._cache.keys()),
            "transactions": list(self._transactions.keys()),
            "connections": list(self._connections.keys()),
        }
