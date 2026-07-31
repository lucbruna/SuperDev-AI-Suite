"""Tests for the messaging subsystem (messaging/)."""

from __future__ import annotations

from typing import Any

import pytest

from integration.messaging.broker import MessageBroker
from integration.messaging.messaging_engine import MessagingEngine
from integration.messaging.protocol import MessageProtocol
from integration.messaging.serializer import MessageSerializer
from integration.messaging.topic_manager import TopicManager


class TestTopicManager:
    def test_create_and_info(self) -> None:
        topics = TopicManager()
        topics.create("orders", "order events")
        assert topics.has("orders") is True
        info = topics.info("orders")
        assert info["description"] == "order events"
        assert topics.count_messages("orders") == 0

    def test_duplicate_raises(self) -> None:
        topics = TopicManager()
        topics.create("orders")
        with pytest.raises(ValueError):
            topics.create("orders")

    def test_list_and_missing(self) -> None:
        topics = TopicManager()
        topics.create("b")
        topics.create("a")
        assert topics.list() == ["a", "b"]
        with pytest.raises(KeyError):
            topics.info("missing")
        assert topics.count_messages("missing") == 0

    def test_increment(self) -> None:
        topics = TopicManager()
        topics.create("t")
        topics.increment("t")
        topics.increment("t")
        assert topics.count_messages("t") == 2


class TestMessageBroker:
    def test_publish_delivers_to_subscribers(self) -> None:
        broker = MessageBroker()
        seen: list[dict[str, Any]] = []
        broker.subscribe("orders", lambda m: seen.append(m))
        message_id = broker.publish("orders", {"order_id": "1"})
        assert message_id
        assert len(seen) == 1
        assert seen[0]["topic"] == "orders"
        assert broker.subscriber_count("orders") == 1

    def test_auto_create_topic(self) -> None:
        broker = MessageBroker()
        broker.publish("new.topic", {"x": 1})
        assert broker.topics.has("new.topic") is True
        assert broker.topics.count_messages("new.topic") == 1

    def test_history_filter(self) -> None:
        broker = MessageBroker()
        broker.publish("a", {"n": 1})
        broker.publish("b", {"n": 2})
        assert len(broker.history()) == 2
        assert len(broker.history(topic="a")) == 1
        assert broker.history(topic="a")[0]["topic"] == "a"


class TestMessageSerializer:
    def test_roundtrip(self) -> None:
        serializer = MessageSerializer()
        payload = {"order_id": "1", "amount": 99.5, "tags": ["a", "b"]}
        assert serializer.roundtrip(payload) == payload
        data = serializer.serialize(payload)
        assert isinstance(data, bytes)


class TestMessageProtocol:
    def test_envelope(self) -> None:
        envelope = MessageProtocol.envelope("orders", {"id": 1}, message_type="command")
        assert envelope["topic"] == "orders"
        assert envelope["type"] == "command"
        assert envelope["version"] == "1.0"
        assert MessageProtocol.validate(envelope) is True
        assert MessageProtocol.topic_of(envelope) == "orders"

    def test_validate_missing_fields(self) -> None:
        assert MessageProtocol.validate({"topic": "x"}) is False


class TestMessagingEngine:
    def test_send_and_stats(self) -> None:
        engine = MessagingEngine()
        seen: list[dict[str, Any]] = []
        engine.create_topic("orders", "order events")
        engine.subscribe("orders", lambda m: seen.append(m))
        message_id = engine.send("orders", {"order_id": "1"})
        assert message_id
        assert len(seen) == 1
        assert seen[0]["type"] == "event"
        assert MessageProtocol.validate(seen[0]) is True
        assert engine.stats()["topics"] == 1
        assert engine.stats()["messages"] == 1
