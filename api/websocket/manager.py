from __future__ import annotations

import time
from typing import Any

from .connection import WebSocketConnection
from .protocol import serialize_message


class ConnectionManager:
    """Manages all active WebSocket connections."""

    def __init__(self) -> None:
        self._connections: dict[str, WebSocketConnection] = {}
        self._handles: dict[str, Any] = {}

    def register(self, connection_id: str, connection: WebSocketConnection, handle: Any = None) -> None:
        self._connections[connection_id] = connection
        if handle is not None:
            self._handles[connection_id] = handle

    def unregister(self, connection_id: str) -> None:
        conn = self._connections.pop(connection_id, None)
        if conn:
            conn.mark_closed()
        self._handles.pop(connection_id, None)

    def get_connection(self, connection_id: str) -> WebSocketConnection | None:
        return self._connections.get(connection_id)

    def get_handle(self, connection_id: str) -> Any:
        return self._handles.get(connection_id)

    async def send_to(self, connection_id: str, message: Any) -> bool:
        handle = self._handles.get(connection_id)
        if handle is None:
            return False
        payload = serialize_message(message)
        try:
            if hasattr(handle, "send"):
                await handle.send(payload)
            return True
        except Exception:
            self.unregister(connection_id)
            return False

    async def broadcast(self, message: Any, exclude: set[str] | None = None) -> int:
        exclude_ids = exclude or set()
        payload = serialize_message(message)
        sent = 0
        for conn_id, handle in list(self._handles.items()):
            if conn_id in exclude_ids:
                continue
            try:
                if hasattr(handle, "send"):
                    await handle.send(payload)
                sent += 1
            except Exception:
                self.unregister(conn_id)
        return sent

    def get_active_connections(self) -> list[WebSocketConnection]:
        return [c for c in self._connections.values() if c.is_alive]

    def get_connection_count(self) -> int:
        return len(self._connections)

    def get_active_count(self) -> int:
        return sum(1 for c in self._connections.values() if c.is_alive)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_connections": self.get_connection_count(),
            "active_connections": self.get_active_count(),
            "connections": [c.to_dict() for c in self._connections.values()],
        }
