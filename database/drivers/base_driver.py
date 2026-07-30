from __future__ import annotations

from typing import Any

from ..database_interfaces import IDatabaseDriver
from ..database_logger import DatabaseLogger
from ..database_models import ColumnMetadata, ConnectionConfig, QueryResult


class BaseDriver(IDatabaseDriver):
    """Abstract base driver with shared connection state and logging."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._connected = False
        self._config: ConnectionConfig | None = None
        self._logger = logger or DatabaseLogger(f"driver.{self.__class__.__name__.lower()}")

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        self._connected = True
        self._logger.info(f"Connected to {config.driver_type.value} at {config.host}:{config.port}")

    async def disconnect(self) -> None:
        self._connected = False
        self._logger.info("Disconnected")

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        raise NotImplementedError

    async def execute_many(self, query: str, params: list[list[Any]]) -> list[QueryResult]:
        results: list[QueryResult] = []
        for param_set in params:
            results.append(await self.execute(query, param_set))
        return results

    async def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        result = await self.execute(query, params)
        return result.rows

    async def begin(self) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def dialect(self) -> str:
        return "generic"

    async def ping(self) -> bool:
        return self._connected

    def get_schema(self, table: str) -> list[ColumnMetadata]:
        raise NotImplementedError

    def _require_connection(self) -> None:
        if not self._connected:
            raise ConnectionError("Driver is not connected")
