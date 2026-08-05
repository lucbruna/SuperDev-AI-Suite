"""MQTT Bridge — pub/sub topics over in-memory storage (no broker)."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.message_bus.kafka_bridge import get_kafka_bridge


class MQTTBridge:
    """MQTT-style topics backed by the local bus."""

    def publish(self, topic: str, payload: dict[str, Any]) -> dict[str, Any]:
        return get_kafka_bridge().produce(f"mqtt/{topic}", payload)

    def subscribe(self, topic: str) -> dict[str, Any]:
        return {"topic": topic, "subscribed": True}

    def poll(self, topic: str) -> dict[str, Any]:
        return get_kafka_bridge().consume(f"mqtt/{topic}")


_mqtt_bridge: MQTTBridge | None = None


def get_mqtt_bridge() -> MQTTBridge:
    global _mqtt_bridge
    if _mqtt_bridge is None:
        _mqtt_bridge = MQTTBridge()
    return _mqtt_bridge
