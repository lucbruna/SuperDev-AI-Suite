from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Protocol

from .database_models import (
    ColumnMetadata,
    ConnectionConfig,
    DatabaseConfig,
    EntityMetadata,
    IndexMetadata,
    MigrationInfo,
    PoolConfig,
    QueryResult,
    TransactionInfo,
)


class IDatabaseDriver(ABC):
    """Abstract interface for all database drivers."""

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> None:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        ...

    @abstractmethod
    async def execute_many(self, query: str, params: list[list[Any]]) -> list[QueryResult]:
        ...

    @abstractmethod
    async def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def begin(self) -> None:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool: ...

    @property
    @abstractmethod
    def dialect(self) -> str: ...

    @abstractmethod
    async def ping(self) -> bool:
        ...

    @abstractmethod
    def get_schema(self, table: str) -> list[ColumnMetadata]:
        ...


class IDatabaseEngine(ABC):
    """Central engine orchestrating drivers, sessions, and lifecycle."""

    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def stop(self) -> None:
        ...

    @abstractmethod
    def get_driver(self, name: str) -> IDatabaseDriver:
        ...

    @abstractmethod
    def register_driver(self, name: str, driver: IDatabaseDriver) -> None:
        ...

    @abstractmethod
    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        ...

    @abstractmethod
    async def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        ...

    @property
    @abstractmethod
    def config(self) -> DatabaseConfig: ...


class IConnectionPool(ABC):
    """Abstract connection pool interface."""

    @abstractmethod
    async def acquire(self) -> Any:
        ...

    @abstractmethod
    async def release(self, conn: Any) -> None:
        ...

    @abstractmethod
    async def status(self) -> dict[str, Any]:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...


class ITransactionManager(ABC):
    """Abstract transaction manager interface."""

    @abstractmethod
    async def begin(self) -> TransactionInfo:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...

    @abstractmethod
    async def savepoint(self, name: str) -> None:
        ...

    @abstractmethod
    async def rollback_to_savepoint(self, name: str) -> None:
        ...

    @abstractmethod
    async def release_savepoint(self, name: str) -> None:
        ...

    @property
    @abstractmethod
    def in_transaction(self) -> bool: ...


class IMigrationEngine(ABC):
    """Abstract migration engine interface."""

    @abstractmethod
    async def create(self, name: str) -> str:
        ...

    @abstractmethod
    async def run(self, target: str | None = None) -> list[MigrationInfo]:
        ...

    @abstractmethod
    async def rollback(self, steps: int = 1) -> list[MigrationInfo]:
        ...

    @abstractmethod
    async def history(self) -> list[MigrationInfo]:
        ...


class ICacheEngine(ABC):
    """Abstract cache engine interface."""

    @abstractmethod
    async def get(self, key: str) -> Any:
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        ...

    @abstractmethod
    async def clear(self) -> None:
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        ...


class IRepository(ABC):
    """Abstract base repository interface."""

    @abstractmethod
    async def get(self, id: Any) -> Any | None:
        ...

    @abstractmethod
    async def list(self, filters: dict[str, Any] | None = None) -> list[Any]:
        ...

    @abstractmethod
    async def create(self, entity: Any) -> Any:
        ...

    @abstractmethod
    async def update(self, entity: Any) -> Any:
        ...

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        ...

    @abstractmethod
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        ...


class IQueryBuilder(ABC):
    """Abstract query builder interface."""

    @abstractmethod
    def select(self, *fields: str) -> IQueryBuilder:
        ...

    @abstractmethod
    def from_table(self, table: str) -> IQueryBuilder:
        ...

    @abstractmethod
    def insert(self, table: str) -> IQueryBuilder:
        ...

    @abstractmethod
    def update(self, table: str) -> IQueryBuilder:
        ...

    @abstractmethod
    def delete(self, table: str) -> IQueryBuilder:
        ...

    @abstractmethod
    def where(self, condition: str, *params: Any) -> IQueryBuilder:
        ...

    @abstractmethod
    def order_by(self, field: str, direction: str = "ASC") -> IQueryBuilder:
        ...

    @abstractmethod
    def limit(self, count: int) -> IQueryBuilder:
        ...

    @abstractmethod
    def offset(self, count: int) -> IQueryBuilder:
        ...

    @abstractmethod
    def join(self, table: str, on: str) -> IQueryBuilder:
        ...

    @abstractmethod
    def set_values(self, values: dict[str, Any]) -> IQueryBuilder:
        ...

    @abstractmethod
    def returning(self, *fields: str) -> IQueryBuilder:
        ...

    @abstractmethod
    def build(self) -> tuple[str, list[Any]]:
        ...


class IMigrationHistory(ABC):
    """Abstract migration history tracker."""

    @abstractmethod
    async def record(self, migration: MigrationInfo) -> None:
        ...

    @abstractmethod
    async def get_applied(self) -> list[MigrationInfo]:
        ...

    @abstractmethod
    async def is_applied(self, migration_id: str) -> bool:
        ...


class IDatabaseEventListener(ABC):
    """Listener for database events."""

    @abstractmethod
    async def on_connect(self, driver_name: str) -> None:
        ...

    @abstractmethod
    async def on_disconnect(self, driver_name: str) -> None:
        ...

    @abstractmethod
    async def on_query(self, query: str, duration_ms: float) -> None:
        ...

    @abstractmethod
    async def on_error(self, error: Exception, query: str | None = None) -> None:
        ...

    @abstractmethod
    async def on_migration(self, migration: MigrationInfo) -> None:
        ...


class IDatabaseMetricsCollector(ABC):
    """Abstract metrics collector for database operations."""

    @abstractmethod
    def record_query(self, duration_ms: float, driver: str, success: bool) -> None:
        ...

    @abstractmethod
    def record_connection(self, driver: str) -> None:
        ...

    @abstractmethod
    def record_disconnection(self, driver: str) -> None:
        ...

    @abstractmethod
    def record_pool_stats(self, driver: str, active: int, idle: int, waiting: int) -> None:
        ...

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def reset(self) -> None:
        ...


class IDatabaseHealthChecker(ABC):
    """Abstract health checker for database connections."""

    @abstractmethod
    async def check(self) -> dict[str, Any]:
        ...

    @abstractmethod
    async def check_driver(self, name: str) -> dict[str, Any]:
        ...
