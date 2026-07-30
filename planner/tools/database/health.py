from __future__ import annotations

from typing import Any

from .database_tool import DatabaseTool


class DatabaseHealth:
    """Health checks for database connectivity."""

    def __init__(self, adapter: DatabaseTool):
        self._adapter = adapter

    def ping(self) -> bool:
        try:
            self._adapter.execute("SELECT 1")
            return True
        except Exception:
            return False

    def check_connections(self) -> dict[str, Any]:
        return {
            "connected": self._adapter.is_connected,
            "status": "healthy" if self._adapter.is_connected else "disconnected",
        }

    def replication_lag(self) -> float:
        return 0.0

    def metrics(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "connected": self._adapter.is_connected,
        }
