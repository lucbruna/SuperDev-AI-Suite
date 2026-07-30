from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

from .database_tool import DatabaseTool


class ConnectionPool:
    """Simple connection pool for database connections."""

    def __init__(self, factory: type[DatabaseTool], min_size: int = 2, max_size: int = 10):
        self._factory = factory
        self._min = min_size
        self._max = max_size
        self._pool: list[DatabaseTool] = []
        self._in_use: set[int] = set()

    def acquire(self) -> DatabaseTool:
        if self._pool:
            conn = self._pool.pop()
            self._in_use.add(id(conn))
            return conn
        conn = self._factory()
        conn.connect()
        self._in_use.add(id(conn))
        return conn

    def release(self, conn: DatabaseTool) -> None:
        self._in_use.discard(id(conn))
        if len(self._pool) < self._max:
            self._pool.append(conn)

    @contextmanager
    def using(self) -> Generator[DatabaseTool, None, None]:
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)

    def close_all(self) -> None:
        for conn in self._pool:
            conn.disconnect()
        self._pool.clear()
        self._in_use.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "pool_size": len(self._pool),
            "in_use": len(self._in_use),
            "min": self._min,
            "max": self._max,
        }
