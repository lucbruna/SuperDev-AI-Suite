"""NATS Bridge — subject-based pub/sub over in-memory storage (no server)."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.message_bus.kafka_bridge import get_kafka_bridge


class NATSBridge:
    """NATS-style subjects backed by the local bus."""

    def publish(self, subject: str, payload: dict[str, Any]) -> dict[str, Any]:
        return get_kafka_bridge().produce(f"nats/{subject}", payload)

    def request(self, subject: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.publish(subject, payload)
        return {"subject": subject, "replied": True}

    def subscribe(self, subject: str) -> dict[str, Any]:
        return {"subject": subject, "subscribed": True}

    def next(self, subject: str) -> dict[str, Any]:
        return get_kafka_bridge().consume(f"nats/{subject}")


_nats_bridge: NATSBridge | None = None


def get_nats_bridge() -> NATSBridge:
    global _nats_bridge
    if _nats_bridge is None:
        _nats_bridge = NATSBridge()
    return _nats_bridge
