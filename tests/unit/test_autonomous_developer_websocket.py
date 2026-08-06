"""Tests for the websocket protocol and simulated hub (Phase H)."""
from __future__ import annotations

from modules.autonomous_developer.websocket import (
    MessageBuilder,
    WebSocketHub,
    WebSocketMessage,
    decode,
    encode,
)


class TestMessageProtocol:
    def test_encode_decode_roundtrip(self):
        message = WebSocketMessage(type="event", payload={"n": 1})
        restored = decode(encode(message))
        assert restored.type == "event"
        assert restored.payload == {"n": 1}
        assert restored.message_id == message.message_id

    def test_decode_missing_payload(self):
        restored = decode('{"type": "ping", "message_id": "m1"}')
        assert restored.type == "ping"
        assert restored.payload == {}
        assert restored.message_id == "m1"

    def test_message_id_unique(self):
        assert WebSocketMessage(type="a").message_id != WebSocketMessage(type="a").message_id

    def test_builder(self):
        assert MessageBuilder.progress({"p": 1}).type == "progress"
        assert MessageBuilder.event({"p": 1}).type == "event"
        assert MessageBuilder.result({"p": 1}).type == "result"


class TestWebSocketHub:
    def test_connect_disconnect_clients(self):
        hub = WebSocketHub()
        assert hub.connect("a") is True
        assert hub.connect("a") is False  # idempotent
        assert hub.clients() == ["a"]
        assert hub.disconnect("a") is True
        assert hub.disconnect("a") is False
        assert hub.clients() == []

    def test_clients_sorted(self):
        hub = WebSocketHub()
        hub.connect("b")
        hub.connect("a")
        assert hub.clients() == ["a", "b"]

    def test_send_and_count(self):
        hub = WebSocketHub()
        hub.send(WebSocketMessage(type="x"))
        assert hub.count() == 1

    def test_broadcast(self):
        hub = WebSocketHub()
        message = hub.broadcast("progress", {"p": 0.5})
        assert message.type == "progress"
        assert message.payload == {"p": 0.5}
        assert hub.count() == 1

    def test_poll_drains(self):
        hub = WebSocketHub()
        hub.broadcast("a")
        hub.broadcast("b")
        pending = hub.poll()
        assert [m.type for m in pending] == ["a", "b"]
        assert hub.count() == 0
