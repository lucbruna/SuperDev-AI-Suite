from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class DatabaseConnection(BaseTool):
    """Manage database connections."""

    _name = "database_connection"
    _description = "Manage database connections: connect, disconnect, ping, status"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._connections: dict[str, dict[str, Any]] = {}

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        conn_id = params.get("connection_id", "default")
        try:
            if action == "connect":
                conn = {
                    "connection_id": conn_id,
                    "host": params.get("host", "localhost"),
                    "port": params.get("port", 5432),
                    "database": params.get("database", ""),
                    "connected": True,
                }
                self._connections[conn_id] = conn
                return {"success": True, "connection": conn}
            elif action == "disconnect":
                self._connections.pop(conn_id, None)
                return {"success": True, "message": f"Disconnected {conn_id}"}
            elif action == "ping":
                conn = self._connections.get(conn_id)
                if not conn:
                    return {"success": False, "error": "Not connected"}
                return {"success": True, "message": "Pong", "latency_ms": 5}
            elif action == "status":
                conn = self._connections.get(conn_id)
                if not conn:
                    return {"success": False, "error": "Not connected"}
                return {"success": True, "connection": conn, "status": "connected"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._connections.clear()

    async def cleanup(self) -> None:
        self._connections.clear()
