from __future__ import annotations

from typing import Any

from .database_tool import DatabaseTool


class MySQLAdapter(DatabaseTool):
    """MySQL database adapter."""

    def __init__(self, connection_string: str = "mysql://localhost:3306/db"):
        super().__init__(connection_string)
        self._conn: Any = None

    def connect(self) -> None:
        # In production: pymysql.connect(...)
        self._connected = True

    def disconnect(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
        self._conn = None
        self._connected = False

    def execute(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return [{"result": f"mysql: {query[:50]}"}]

    def get_databases(self) -> list[str]:
        return []

    def get_tables(self, database: str = "") -> list[str]:
        return []
