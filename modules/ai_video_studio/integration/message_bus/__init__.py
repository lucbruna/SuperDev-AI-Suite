"""Message Bus — Kafka, RabbitMQ, Redis Streams, NATS and MQTT bridges."""
from modules.ai_video_studio.integration.message_bus.kafka_bridge import (
    KafkaBridge,
    get_kafka_bridge,
)
from modules.ai_video_studio.integration.message_bus.message_bus_connector import (
    MessageBusConnector,
    get_message_bus_connector,
)
from modules.ai_video_studio.integration.message_bus.rabbitmq_bridge import (
    RabbitMQBridge,
    get_rabbitmq_bridge,
)

__all__ = [
    "KafkaBridge",
    "get_kafka_bridge",
    "RabbitMQBridge",
    "get_rabbitmq_bridge",
    "MessageBusConnector",
    "get_message_bus_connector",
]
