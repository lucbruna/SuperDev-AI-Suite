"""Tests for the communication/ subpackage (Volume 31, Fase 3)."""

from __future__ import annotations

from agent_orchestration.communication import (AgentChat, CommunicationEngine,
                                               EventRouter, MessageBus,
                                               ProtocolManager)
from agent_orchestration.orchestrator_events import OrchestratorEventType
from agent_orchestration.orchestrator_models import MessageType


class TestMessageBus:
    def test_send_delivers_to_inbox(self):
        bus = MessageBus()
        bus.send("alice", "bob", "oi bob")
        inbox = bus.inbox("bob")
        assert len(inbox) == 1
        assert inbox[0].content == "oi bob"
        assert inbox[0].sender_id == "alice"

    def test_broadcast_reaches_all_inboxes(self):
        bus = MessageBus()
        bus.inbox("bob")
        bus.inbox("carol")
        bus.send("alice", "all", "olá todos", MessageType.BROADCAST)
        assert len(bus.inbox("bob")) == 1
        assert len(bus.inbox("carol")) == 1

    def test_history_and_count(self):
        bus = MessageBus()
        bus.send("a", "b", "m1")
        bus.send("b", "a", "m2")
        assert bus.count() == 2
        assert len(bus.history()) == 2

    def test_between_filter(self):
        bus = MessageBus()
        bus.send("a", "b", "m1")
        bus.send("a", "c", "m2")
        between = bus.between("a", "b")
        assert len(between) == 1
        assert between[0].recipient_id == "b"


class TestAgentChat:
    def test_conversation_round_trip(self):
        chat = AgentChat("alice", "bob")
        chat.say("alice", "oi")
        chat.say("bob", "olá")
        assert chat.count() == 2
        assert chat.transcript() == ["alice: oi", "bob: olá"]

    def test_sender_normalized_to_partner(self):
        chat = AgentChat("alice", "bob")
        chat.say("bob", "oi alice")
        assert chat.messages()[0].recipient_id == "alice"


class TestEventRouter:
    def test_route_calls_registered_handlers(self):
        router = EventRouter()
        seen: list[str] = []
        router.on(OrchestratorEventType.MESSAGE_SENT,
                  lambda payload: seen.append("a"))
        router.on(OrchestratorEventType.MESSAGE_SENT,
                  lambda payload: seen.append("b"))
        router.route(OrchestratorEventType.MESSAGE_SENT, {})
        assert seen == ["a", "b"]

    def test_handler_error_isolated(self):
        router = EventRouter()

        def failing(payload):
            raise RuntimeError("boom")

        router.on(OrchestratorEventType.MESSAGE_SENT, failing)
        results = router.route(OrchestratorEventType.MESSAGE_SENT, {})
        assert results[0]["ok"] is False
        assert "boom" in results[0]["error"]

    def test_off_removes_handler(self):
        router = EventRouter()

        def handler(payload):
            pass

        router.on(OrchestratorEventType.MESSAGE_SENT, handler)
        router.off(OrchestratorEventType.MESSAGE_SENT, handler)
        assert router.counts() == {}

    def test_route_to_other_type_noop(self):
        router = EventRouter()
        seen: list[str] = []
        router.on(OrchestratorEventType.TASK_STARTED,
                  lambda payload: seen.append("t"))
        router.route(OrchestratorEventType.MESSAGE_SENT, {})
        assert seen == []


class TestProtocolManager:
    def test_supported_types(self):
        protocols = ProtocolManager()
        assert protocols.message_supported(MessageType.DIRECT) is True
        assert protocols.message_supported(MessageType.EVENT) is True

    def test_validate_required_fields(self):
        protocols = ProtocolManager()
        assert protocols.validate(MessageType.EVENT,
                                 {"event": "x", "payload": {}}) is True
        assert protocols.validate(MessageType.EVENT, {}) is False

    def test_register_and_list_protocols(self):
        protocols = ProtocolManager()
        protocols.register_protocol("llm", version="1.1")
        assert "llm" in protocols.protocols()

    def test_describe(self):
        description = ProtocolManager().describe(MessageType.DIRECT)
        assert description["type"] == "direct"
        assert "content" in description["fields"]


class TestCommunicationEngine:
    def test_send_increments_metrics_and_publishes_event(self):
        engine = CommunicationEngine()
        seen: list[str] = []
        engine.on(OrchestratorEventType.MESSAGE_SENT,
                  lambda payload: seen.append(payload["message_id"]))
        message = engine.send("alice", "bob", "oi")
        assert message is not None
        assert engine.bus.count() == 1
        assert engine.metrics.snapshot()["counters"].get("ao.messages") == 1
        assert len(seen) == 1

    def test_protocol_violation_rejected(self):
        engine = CommunicationEngine()
        message = engine.send("alice", "bob", "x",
                              MessageType.EVENT, {"event": "e", "payload": {}})
        assert message is not None
        bad = engine.send("alice", "bob", "x", MessageType.EVENT, {})
        assert bad is None
        assert engine.metrics.snapshot()["counters"].get(
            "ao.protocol_violations") == 1

    def test_chat_facade(self):
        engine = CommunicationEngine()
        chat = engine.chat("alice", "bob")
        chat.say("alice", "oi")
        assert len(engine.inbox("bob")) == 1
        assert len(engine.history()) == 1

    def test_stats(self):
        engine = CommunicationEngine()
        engine.send("alice", "bob", "oi")
        stats = engine.stats()
        assert stats["messages"] == 1
        assert "ao.messages" in stats["metrics"]

    def test_protocols_registered_via_facade(self):
        engine = CommunicationEngine()
        engine.protocols.register_protocol("custom")
        assert "custom" in engine.stats()["protocols"]
