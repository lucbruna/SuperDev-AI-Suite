from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str = "default") -> None:
        await websocket.accept()
        async with self._lock:
            if channel not in self.active_connections:
                self.active_connections[channel] = []
            self.active_connections[channel].append(websocket)

    async def disconnect(self, websocket: WebSocket, channel: str = "default") -> None:
        async with self._lock:
            if channel in self.active_connections:
                self.active_connections[channel] = [
                    conn for conn in self.active_connections[channel] if conn != websocket
                ]
                if not self.active_connections[channel]:
                    del self.active_connections[channel]

    async def send_personal(self, data: dict[str, Any], websocket: WebSocket) -> None:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(json.dumps(data))

    async def broadcast(self, channel: str, data: dict[str, Any]) -> None:
        connections = self.active_connections.get(channel, [])
        disconnected = []
        for connection in connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(json.dumps(data))
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            await self.disconnect(conn, channel)

    async def broadcast_all(self, data: dict[str, Any]) -> None:
        for channel in list(self.active_connections.keys()):
            await self.broadcast(channel, data)

    def get_connections(self, channel: str = "default") -> list[WebSocket]:
        return self.active_connections.get(channel, [])

    def get_connection_count(self, channel: str | None = None) -> int:
        if channel:
            return len(self.active_connections.get(channel, []))
        return sum(len(conns) for conns in self.active_connections.values())


manager = ConnectionManager()
