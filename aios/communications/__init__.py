"""AIOS Communications — platform messaging subsystem.

Provides the event bus (pub/sub), typed message router, and transport
adapters: gRPC, REST, WebSocket, MQTT, Kafka bridge and Redis Streams.
All adapters are deterministic, in-memory and dependency-free; real
transports can be plugged in behind the same contracts.
"""

from __future__ import annotations

from .event_bus import EventBus
from .grpc_manager import GRPCManager
from .kafka_bridge import KafkaBridge
from .message_router import MessageRouter
from .mqtt_gateway import MQTTGateway
from .redis_streams import RedisStreams
from .rest_gateway import RESTGateway
from .websocket_gateway import WebSocketGateway

__all__ = [
    "EventBus",
    "MessageRouter",
    "GRPCManager",
    "RESTGateway",
    "WebSocketGateway",
    "MQTTGateway",
    "KafkaBridge",
    "RedisStreams",
]
