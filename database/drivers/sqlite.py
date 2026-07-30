from __future__ import annotations

import sqlite3
import threading
import time
from typing import Any

from ..database_models import ColumnMetadata, ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class SQLiteDriver(BaseDriver):
    """SQLite driver using stdlib sqlite3 module.

    Full implementation — the only driver with zero external dependencies
    since sqlite3 is part of Python stdlib.
    """

    def __init__(self, logger: Any = None) -> None:
        super().__init__(logger)
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()
        self._transactions = 0

    async def connect(self, config: ConnectionConfig) -> None:
        db_path = config.database or config.dsn or ":memory:"
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._connected = True
        self._config = config
        self._logger.info(f"SQLite connected: {db_path}")

    async def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
        self._connected = False
        self._logger.info("SQLite disconnected")

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        start = time.monotonic()
        with self._lock:
            cursor = self._conn.execute(query, params or [])
            rows = [dict(row) for row in cursor.fetchall()] if cursor.description else []
            self._conn.commit()
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(
                rows=rows,
                row_count=len(rows) if cursor.description else cursor.rowcount,
                columns=[desc[0] for desc in cursor.description] if cursor.description else [],
                duration_ms=round(elapsed, 2),
                last_insert_id=cursor.lastrowid,
            )

    async def execute_many(self, query: str, params: list[list[Any]]) -> list[QueryResult]:
        self._require_connection()
        results: list[QueryResult] = []
        with self._lock:
            for param_set in params:
                cursor = self._conn.execute(query, param_set)
                rows = [dict(row) for row in cursor.fetchall()] if cursor.description else []
                results.append(QueryResult(
                    rows=rows,
                    row_count=len(rows) if cursor.description else cursor.rowcount,
                    duration_ms=0.0,
                ))
            self._conn.commit()
        return results

    async def begin(self) -> None:
        self._require_connection()
        with self._lock:
            self._conn.execute("BEGIN")
            self._transactions += 1

    async def commit(self) -> None:
        self._require_connection()
        with self._lock:
            self._conn.commit()
            self._transactions -= 1

    async def rollback(self) -> None:
        self._require_connection()
        with self._lock:
            self._conn.rollback()
            self._transactions -= 1

    @property
    def dialect(self) -> str:
        return "sqlite"

    async def ping(self) -> bool:
        try:
            if not self._conn:
                return False
            self._conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    def get_schema(self, table: str) -> list[ColumnMetadata]:
        self._require_connection()
        cursor = self._conn.execute(f"PRAGMA table_info({table})")
        columns: list[ColumnMetadata] = []
        for row in cursor.fetchall():
            columns.append(ColumnMetadata(
                name=row["name"],
                data_type=row["type"],
                nullable=not row["notnull"],
                is_pk=bool(row["pk"]),
                default=row["dflt_value"],
            ))
        return columns
