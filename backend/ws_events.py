"""Sistema de eventos WebSocket para comunicação em tempo real."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class WsEvent:
    """Evento WebSocket padronizado."""

    def __init__(self, event_type: str, data: dict[str, Any], room: str = "default", sender: str | None = None) -> None:
        self.id = str(uuid4())
        self.type = event_type
        self.data = data
        self.room = room
        self.sender = sender
        self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "data": self.data, "room": self.room, "sender": self.sender, "timestamp": self.timestamp}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class WsManager:
    """Gerenciador de conexões WebSocket."""

    def __init__(self) -> None:
        self._connections: dict[str, Any] = {}
        self._rooms: dict[str, set[str]] = {}
        self._event_history: list[WsEvent] = []

    async def connect(self, websocket: Any, client_id: str | None = None) -> str:
        await websocket.accept()
        if client_id is None:
            client_id = str(uuid4())
        self._connections[client_id] = websocket
        return client_id

    def disconnect(self, client_id: str) -> None:
        self._connections.pop(client_id, None)
        for room_clients in self._rooms.values():
            room_clients.discard(client_id)

    async def join_room(self, client_id: str, room: str) -> None:
        if room not in self._rooms:
            self._rooms[room] = set()
        self._rooms[room].add(client_id)

    async def leave_room(self, client_id: str, room: str) -> None:
        if room in self._rooms:
            self._rooms[room].discard(client_id)

    async def send_to_room(self, room: str, event: WsEvent) -> None:
        if room in self._rooms:
            for client_id in list(self._rooms[room]):
                if client_id in self._connections:
                    try:
                        await self._connections[client_id].send_text(event.to_json())
                    except Exception:
                        self.disconnect(client_id)

    async def broadcast(self, event: WsEvent) -> None:
        disconnected = []
        for client_id, ws in self._connections.items():
            try:
                await ws.send_text(event.to_json())
            except Exception:
                disconnected.append(client_id)
        for cid in disconnected:
            self.disconnect(cid)

    def get_connected_clients(self) -> list[str]:
        return list(self._connections.keys())


ws_manager = WsManager()
