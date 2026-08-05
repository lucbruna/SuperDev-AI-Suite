"""Message Bus Connector — facade over the broker bridges."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.message_bus.kafka_bridge import (
    get_kafka_bridge,
)
from modules.ai_video_studio.integration.message_bus.mqtt_bridge import get_mqtt_bridge
from modules.ai_video_studio.integration.message_bus.nats_bridge import get_nats_bridge
from modules.ai_video_studio.integration.message_bus.rabbitmq_bridge import (
    get_rabbitmq_bridge,
)
from modules.ai_video_studio.integration.message_bus.redis_streams import (
    get_redis_streams,
)


class MessageBusConnector(DomainConnector):
    """Kafka, RabbitMQ, Redis Streams, NATS and MQTT bridges."""

    domain = "message_bus"
    description = "Kafka, RabbitMQ, Redis Streams, NATS and MQTT bridges"

    def __init__(self) -> None:
        super().__init__()
        self._register("kafka_produce", lambda d: get_kafka_bridge().produce(
            d.get("topic", "default"), d.get("message", {})))
        self._register("rabbitmq_publish", lambda d: get_rabbitmq_bridge().publish(
            d.get("queue", "default"), d.get("message", {})))
        self._register("stream_add", lambda d: get_redis_streams().add(
            d.get("stream", "default"), d.get("fields", {})))
        self._register("nats_publish", lambda d: get_nats_bridge().publish(
            d.get("subject", "default"), d.get("payload", {})))
        self._register("mqtt_publish", lambda d: get_mqtt_bridge().publish(
            d.get("topic", "default"), d.get("payload", {})))
        self._register("bus_status", lambda d: self._status())

    def _status(self) -> dict[str, Any]:
        return {"kafka": get_kafka_bridge().topics(), "redis_streams": get_redis_streams().read("default")}


_message_bus_connector: MessageBusConnector | None = None


def get_message_bus_connector() -> MessageBusConnector:
    global _message_bus_connector
    if _message_bus_connector is None:
        _message_bus_connector = MessageBusConnector()
    return _message_bus_connector
