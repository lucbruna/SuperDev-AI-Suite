"""In-memory message broker."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable

from .topic_manager import TopicManager


class MessageBroker:
    """Routes messages between producers and consumers per topic."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.messaging.broker")
        self.topics = TopicManager()
        self._subscriptions: dict[str, list[Callable[[dict[str, Any]], None]]] = {}
        self._history: list[dict[str, Any]] = []

    def ensure_topic(self, topic: str) -> None:
        if not self.topics.has(topic):
            self.topics.create(topic)

    def subscribe(self, topic: str, handler: Callable[[dict[str, Any]], None]) -> None:
        self.ensure_topic(topic)
        self._subscriptions.setdefault(topic, []).append(handler)

    def publish(self, topic: str, payload: dict[str, Any]) -> str:
        self.ensure_topic(topic)
        message_id = str(uuid.uuid4())
        message: dict[str, Any] = {
            "message_id": message_id,
            "topic": topic,
            "payload": payload,
        }
        self.topics.increment(topic)
        self._history.append(message)
        for handler in self._subscriptions.get(topic, []):
            handler(message)
        return message_id

    def history(self, topic: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        messages = self._history
        if topic is not None:
            messages = [m for m in messages if m["topic"] == topic]
        return list(messages[-limit:])

    def subscriber_count(self, topic: str) -> int:
        return len(self._subscriptions.get(topic, []))
