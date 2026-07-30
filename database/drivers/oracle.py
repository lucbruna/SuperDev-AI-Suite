from __future__ import annotations

from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class OracleDriver(BaseDriver):
    """Oracle driver — stdlib has no Oracle client.

    Provides the driver interface. For production use,
    install oracledb or cx_Oracle.
    """

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        self._connected = True
        self._logger.info(f"Oracle configured at {config.host}:{config.port or 1521}")

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        import time
        start = time.monotonic()
        try:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(rows=[], row_count=0, duration_ms=round(elapsed, 2))
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    @property
    def dialect(self) -> str:
        return "oracle"
