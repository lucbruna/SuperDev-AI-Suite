from __future__ import annotations

import json
import time
from typing import Any

from ..api_events import APIEventBus, APIEventType
from ..api_logger import APILogger
from ..api_metrics import APIMetrics
from ..api_registry import APIRegistry
from .connection import WebSocketConnection
from .manager import ConnectionManager
from .rooms import RoomManager
from .security import WSAuthenticator
from .events import handle_message as handle_ws_message


class WebSocketServer:
    """WebSocket server handling connections, messages, and lifecycle."""

    def __init__(
        self,
        registry: APIRegistry,
        logger: APILogger,
        metrics: APIMetrics,
        events: APIEventBus,
    ) -> None:
        self._registry = registry
        self._logger = logger
        self._metrics = metrics
        self._events = events
        self.connections = ConnectionManager()
        self.rooms = RoomManager()
        self.security = WSAuthenticator(logger=logger)
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    async def accept_connection(
        self,
        connection_id: str,
        path: str,
        scope: dict[str, Any],
    ) -> WebSocketConnection | None:
        auth_result = await self.security.authenticate_connection(scope)
        if not auth_result.get("authenticated"):
            self._logger.warning("WebSocket connection rejected", path=path)
            return None

        user_id = auth_result.get("user_id", "")
        conn = WebSocketConnection(connection_id, path, user_id=user_id)
        self.connections.register(connection_id, conn)
        self._metrics.increment("ws.connections")
        await self._events.emit(APIEventType.CONNECTION_OPENED, {
            "connection_id": connection_id,
            "path": path,
            "user_id": user_id,
        })
        return conn

    async def handle_message(self, connection: WebSocketConnection, message: str | bytes) -> dict[str, Any] | None:
        self._metrics.increment("ws.messages")
        result = await handle_ws_message(connection, message, self._registry, self._logger)
        if result:
            await self._events.emit(APIEventType.WEBSOCKET_MESSAGE, {
                "connection_id": connection.connection_id,
                "type": result.get("type", ""),
            })
        return result

    async def disconnect(self, connection_id: str, code: int = 1000, reason: str = "") -> None:
        conn = self.connections.get_connection(connection_id)
        if conn:
            conn.mark_closed(code, reason)
        self.rooms.remove_connection(connection_id)
        self.connections.unregister(connection_id)
        self._metrics.increment("ws.disconnections")
        await self._events.emit(APIEventType.CONNECTION_CLOSED, {
            "connection_id": connection_id,
            "code": code,
            "reason": reason,
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "connections": self.connections.to_dict(),
            "rooms": self.rooms.to_dict(),
            "security": self.security.to_dict(),
        }
