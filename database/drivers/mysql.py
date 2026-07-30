from __future__ import annotations

import asyncio
import time
from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class MySQLDriver(BaseDriver):
    """MySQL driver — stdlib has no MySQL client.

    Provides the driver interface for consistency. For production use,
    install aiomysql or mysql-connector-python and subclass BaseDriver.
    """

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        self._connected = True
        self._logger.info(f"MySQL configured at {config.host}:{config.port or 3306}")

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        start = time.monotonic()
        try:
            elapsed = (time.monotonic() - start) * 1000
            self._logger.query(query, elapsed)
            return QueryResult(rows=[], row_count=0, duration_ms=round(elapsed, 2))
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    async def begin(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass

    @property
    def dialect(self) -> str:
        return "mysql"
