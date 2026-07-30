from __future__ import annotations

import time
from typing import Any

from .protocol import serialize_message


class RoomManager:
    """Manages WebSocket rooms/channels for group messaging."""

    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, Any]] = {}

    def create_room(self, name: str, metadata: dict[str, Any] | None = None) -> bool:
        if name in self._rooms:
            return False
        self._rooms[name] = {
            "name": name,
            "members": {},
            "metadata": metadata or {},
            "created_at": time.time(),
        }
        return True

    def join_room(self, connection_id: str, room_name: str, handle: Any = None) -> bool:
        room = self._rooms.get(room_name)
        if room is None:
            return False
        room["members"][connection_id] = {
            "connection_id": connection_id,
            "handle": handle,
            "joined_at": time.time(),
        }
        return True

    def leave_room(self, connection_id: str, room_name: str) -> bool:
        room = self._rooms.get(room_name)
        if room is None:
            return False
        return room["members"].pop(connection_id, None) is not None

    def remove_connection(self, connection_id: str) -> list[str]:
        left_rooms: list[str] = []
        for room_name, room in list(self._rooms.items()):
            if connection_id in room["members"]:
                room["members"].pop(connection_id, None)
                left_rooms.append(room_name)
        return left_rooms

    async def broadcast_to_room(self, room_name: str, message: Any, exclude: set[str] | None = None) -> int:
        room = self._rooms.get(room_name)
        if room is None:
            return 0
        exclude_ids = exclude or set()
        payload = serialize_message(message)
        sent = 0
        for conn_id, member in list(room["members"].items()):
            if conn_id in exclude_ids:
                continue
            handle = member.get("handle")
            if handle is not None and hasattr(handle, "send"):
                try:
                    await handle.send(payload)
                    sent += 1
                except Exception:
                    room["members"].pop(conn_id, None)
        return sent

    def list_rooms(self) -> dict[str, int]:
        return {name: len(room["members"]) for name, room in self._rooms.items()}

    def get_room_members(self, room_name: str) -> list[str]:
        room = self._rooms.get(room_name)
        return list(room["members"].keys()) if room else []

    def delete_room(self, name: str) -> bool:
        return self._rooms.pop(name, None) is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rooms": self.list_rooms(),
            "total_rooms": len(self._rooms),
        }
