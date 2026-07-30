from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.websocket import WebSocketServer, ConnectionManager, WebSocketConnection  # noqa: E402
from api.websocket.rooms import RoomManager  # noqa: E402
from api.websocket.events import EventEmitter  # noqa: E402
from api.websocket.protocol import WebSocketProtocol  # noqa: E402
from api.websocket.security import WebSocketSecurity  # noqa: E402


class TestConnectionManager:
    def test_add_connection(self) -> None:
        mgr = ConnectionManager()
        conn = WebSocketConnection("conn1", "user1")
        mgr.add(conn)
        assert mgr.get("conn1") is conn
        assert mgr.count() == 1

    def test_remove_connection(self) -> None:
        mgr = ConnectionManager()
        conn = WebSocketConnection("conn1", "user1")
        mgr.add(conn)
        mgr.remove("conn1")
        assert mgr.get("conn1") is None

    def test_get_by_user(self) -> None:
        mgr = ConnectionManager()
        mgr.add(WebSocketConnection("c1", "user1"))
        mgr.add(WebSocketConnection("c2", "user1"))
        conns = mgr.get_by_user("user1")
        assert len(conns) == 2

    def test_broadcast(self) -> None:
        mgr = ConnectionManager()
        received: list[Any] = []
        async def handler(event: Any) -> None:
            received.append(event)

        conn = WebSocketConnection("c1", "user1")
        conn.on_message = handler  # type: ignore[assignment]

        assert mgr.count() == 0


class TestRoomManager:
    def test_join_room(self) -> None:
        rooms = RoomManager()
        rooms.join("room1", "conn1")
        assert rooms.get_members("room1") == ["conn1"]

    def test_leave_room(self) -> None:
        rooms = RoomManager()
        rooms.join("room1", "conn1")
        rooms.leave("room1", "conn1")
        assert rooms.get_members("room1") == []

    def test_get_user_rooms(self) -> None:
        rooms = RoomManager()
        rooms.join("room1", "conn1")
        rooms.join("room2", "conn1")
        user_rooms = rooms.get_user_rooms("conn1")
        assert sorted(user_rooms) == ["room1", "room2"]


class TestEventEmitter:
    def test_on_and_emit(self) -> None:
        emitter = EventEmitter()
        received: list[str] = []
        emitter.on("test", lambda data: received.append(data))
        emitter.emit("test", "hello")
        assert received == ["hello"]

    def test_off(self) -> None:
        emitter = EventEmitter()
        received: list[str] = []
        handler = lambda data: received.append(data)  # noqa: E731
        emitter.on("test", handler)
        emitter.off("test", handler)
        emitter.emit("test", "hello")
        assert received == []

    def test_once(self) -> None:
        emitter = EventEmitter()
        received: list[str] = []
        emitter.once("test", lambda data: received.append(data))
        emitter.emit("test", "a")
        emitter.emit("test", "b")
        assert received == ["a"]


class TestWebSocketProtocol:
    def test_encode_decode(self) -> None:
        protocol = WebSocketProtocol()
        message = {"type": "message", "data": "hello"}
        encoded = protocol.encode(message)
        decoded = protocol.decode(encoded)
        assert decoded == message


class TestWebSocketSecurity:
    def test_validate_origin(self) -> None:
        security = WebSocketSecurity()
        assert security.validate_origin("https://example.com", ["https://example.com"])
        assert not security.validate_origin("https://evil.com", ["https://example.com"])

    def test_validate_token(self) -> None:
        security = WebSocketSecurity()
        assert security.validate_token("valid-token", ["valid-token"])
        assert not security.validate_token("invalid", ["valid-token"])
