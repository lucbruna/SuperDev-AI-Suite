"""Messaging engine: facade over broker, topics, and protocol."""

from __future__ import annotations

import logging
from typing import Any, Callable

from .broker import MessageBroker
from .protocol import MessageProtocol
from .serializer import MessageSerializer


class MessagingEngine:
    """Facade for the messaging subsystem."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.messaging")
        self.broker = MessageBroker()
        self.protocol = MessageProtocol()
        self.serializer = MessageSerializer()

    def create_topic(self, topic: str, description: str = "") -> None:
        self.broker.ensure_topic(topic)
        if description:
            self.broker.topics.info(topic)["description"] = description

    def subscribe(self, topic: str, handler: Callable[[dict[str, Any]], None]) -> None:
        def wrapper(message: dict[str, Any]) -> None:
            # Deliver the protocol envelope to the caller.
            handler(message["payload"])

        self.broker.subscribe(topic, wrapper)

    def send(self, topic: str, payload: dict[str, Any],
             message_type: str = "event") -> str:
        message = self.protocol.envelope(topic, payload, message_type)
        return self.broker.publish(topic, message)

    def stats(self) -> dict[str, Any]:
        return {
            "topics": len(self.broker.topics.list()),
            "messages": len(self.broker.history()),
        }
