"""Message envelope and protocol helpers."""

from __future__ import annotations

import time
import uuid
from typing import Any


class MessageProtocol:
    """Builds and inspects standardized message envelopes."""

    @staticmethod
    def envelope(topic: str, payload: dict[str, Any],
                 message_type: str = "event") -> dict[str, Any]:
        return {
            "message_id": str(uuid.uuid4()),
            "topic": topic,
            "type": message_type,
            "payload": payload,
            "timestamp": time.time(),
            "version": "1.0",
        }

    @staticmethod
    def validate(message: dict[str, Any]) -> bool:
        required = {"message_id", "topic", "type", "payload", "timestamp", "version"}
        return required.issubset(message.keys())

    @staticmethod
    def topic_of(message: dict[str, Any]) -> str:
        return message.get("topic", "")
