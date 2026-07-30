from __future__ import annotations

from ..communication_engine import CommunicationEngine
from ..message_bus import MessageBus
from ..message import Message
from ..envelope import Envelope
from ..broadcast import Broadcast
from ..multicast import Multicast
from ..unicast import Unicast
from ..conversation import Conversation
from ..protocol import Protocol
from ..serializer import Serializer
from ..deserializer import Deserializer
from ..compression import Compression
from ..encryption import Encryption
from ..retry import Retry
from ..acknowledgement import Acknowledgement


class TestMessage:
    def test_create(self) -> None:
        m = Message("a1", "a2", "request", {"data": "hello"})
        assert m.sender == "a1"
        assert m.recipient == "a2"
        assert m.msg_type == "request"

    def test_to_dict(self) -> None:
        m = Message("a1", "a2", "request", {})
        d = m.to_dict()
        assert d["sender"] == "a1"


class TestEnvelope:
    def test_create(self) -> None:
        e = Envelope({"type": "test"}, priority=1)
        assert e.priority == 1

    def test_headers(self) -> None:
        e = Envelope({})
        e.set_header("x-id", "123")
        assert e.get_header("x-id") == "123"


class TestMessageBus:
    def setup_method(self) -> None:
        self.bus = MessageBus()

    def test_send_receive(self) -> None:
        self.bus.send("a1", "a2", {"text": "hi"})
        msgs = self.bus.receive("a2")
        assert len(msgs) == 1

    def test_broadcast(self) -> None:
        self.bus.send("a1", "a2", {})
        self.bus.send("a1", "a3", {})
        count = self.bus.broadcast("a1", {"alert": "test"})
        assert count >= 1

    def test_clear(self) -> None:
        self.bus.send("a1", "a2", {})
        self.bus.clear()
        assert self.bus.message_count == 0


class TestCommunicationEngine:
    def test_send(self) -> None:
        engine = CommunicationEngine()
        msg_id = engine.send("a1", "a2", {"text": "hi"})
        assert msg_id is not None

    def test_receive(self) -> None:
        engine = CommunicationEngine()
        engine.send("a1", "a2", {"text": "hi"})
        msgs = engine.receive("a2")
        assert len(msgs) == 1


class TestBroadcast:
    def test_send(self) -> None:
        b = Broadcast()
        count = b.send("a1", {"msg": "hi"}, ["a2", "a3"])
        assert count == 2
        assert b.broadcast_count == 1


class TestMulticast:
    def test_group(self) -> None:
        m = Multicast()
        m.create_group("dev")
        m.join("dev", "a1")
        m.join("dev", "a2")
        assert len(m.group_members("dev")) == 2

    def test_leave(self) -> None:
        m = Multicast()
        m.create_group("dev")
        m.join("dev", "a1")
        assert m.leave("dev", "a1") is True


class TestUnicast:
    def test_send(self) -> None:
        u = Unicast()
        assert u.send("a1", "a2", {"msg": "hi"}) is True
        assert u.sent_count == 1


class TestConversation:
    def test_add_message(self) -> None:
        c = Conversation("c1", ["a1", "a2"])
        c.add_message("a1", {"text": "hello"})
        assert len(c.messages) == 1

    def test_last_message(self) -> None:
        c = Conversation("c1", ["a1", "a2"])
        c.add_message("a1", {"text": "hello"})
        assert c.last_message() is not None


class TestProtocol:
    def test_validate(self) -> None:
        p = Protocol("test")
        assert p.validate({"sender": "a1", "content": {}})
        assert not p.validate({"content": {}})

    def test_rules(self) -> None:
        p = Protocol("test")
        p.add_rule("max_size", 1024)
        assert p.get_rule("max_size") == 1024


class TestSerializer:
    def test_serialize(self) -> None:
        s = Serializer.serialize({"a": 1})
        assert isinstance(s, str)

    def test_message_to_dict(self) -> None:
        d = Serializer.message_to_dict({"sender": "a1"})
        assert d["sender"] == "a1"


class TestDeserializer:
    def test_deserialize(self) -> None:
        import json
        d = Deserializer.deserialize(json.dumps({"a": 1}))
        assert d["a"] == 1


class TestCompression:
    def test_roundtrip(self) -> None:
        data = "hello world " * 100
        compressed = Compression.compress(data)
        decompressed = Compression.decompress(compressed)
        assert decompressed == data

    def test_dict_roundtrip(self) -> None:
        data = {"key": "value" * 50}
        compressed = Compression.compress_dict(data)
        decompressed = Compression.decompress_dict(compressed)
        assert decompressed == data


class TestEncryption:
    def test_hash(self) -> None:
        h = Encryption.hash_content({"a": 1})
        assert isinstance(h, str)

    def test_obfuscate(self) -> None:
        o = Encryption.obfuscate("secret")
        assert o != "secret"


class TestRetry:
    def test_execute_success(self) -> None:
        r = Retry(max_retries=3)
        result = r.execute(lambda: "ok")
        assert result == "ok"

    def test_reset(self) -> None:
        r = Retry()
        r.execute(lambda: 1)
        r.reset()
        assert r.attempts == 0


class TestAcknowledgement:
    def test_acknowledge(self) -> None:
        a = Acknowledgement()
        a.acknowledge("msg1")
        assert a.is_acknowledged("msg1")

    def test_not_acknowledged(self) -> None:
        a = Acknowledgement()
        assert not a.is_acknowledged("missing")
