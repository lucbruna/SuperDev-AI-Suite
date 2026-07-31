from __future__ import annotations

import sqlite3
import time
from typing import Any

from ..data_models import DataSourceType
from .collector import BaseCollector
from .connector import BaseConnector


class DatabaseConnector(BaseConnector):
    """SQL database connector built on the standard library ``sqlite3``.

    Config keys:
        database: path or ":memory:" (default ":memory:")
        table: default table to read
        query: optional default SQL query
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(name, config)
        self._connection: sqlite3.Connection | None = None

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.DATABASE

    async def connect(self) -> bool:
        try:
            self._connection = sqlite3.connect(self.config.get("database", ":memory:"))
            self.connected = True
            return True
        except sqlite3.Error:
            self.connected = False
            return False

    async def read(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if self._connection is None:
            raise RuntimeError(f"Database connector '{self.name}' is not connected")
        query = query or {}
        sql = query.get("query") or query.get("sql") or self.config.get("query")
        table = query.get("table") or self.config.get("table")
        if sql is None and table:
            sql = f"SELECT * FROM {table}"
        if sql is None:
            raise ValueError(f"Database connector '{self.name}' requires a query or table")

        cursor = self._connection.execute(sql)
        columns = [description[0] for description in cursor.description] if cursor.description else []
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        self._last_read_at = time.time()
        return rows

    async def disconnect(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        self.connected = False


class DatabaseCollector(BaseCollector):
    """Collector that reads rows from a database via :class:`DatabaseConnector`."""

    def __init__(
        self,
        name: str,
        connector: DatabaseConnector | None = None,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, engine, config)
        self.connector = connector or DatabaseConnector(name, config or {})

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.DATABASE

    async def collect(self, config: dict[str, Any] | None = None) -> Any:
        merged = {**self.config, **(config or {})}
        await self.connector.connect()
        try:
            rows = await self.connector.read(merged)
        finally:
            await self.connector.disconnect()
        return self._build_batch(rows, metadata={"connector": "database"})


__all__ = ["DatabaseConnector", "DatabaseCollector"]
