"""Data Platform Protocols — Protocol definitions for data platform operations."""

from dataclasses import dataclass, field
from enum import Enum


class DataProtocolType(Enum):
    REST = "rest"
    GRPC = "grpc"
    KAFKA = "kafka"
    AMQP = "amqp"
    MQTT = "mqtt"
    WEBSOCKET = "websocket"


@dataclass
class DataProtocolConfig:
    name: str
    protocol_type: DataProtocolType = DataProtocolType.REST
    version: str = "1.0"
    base_url: str = ""
    authentication: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_count: int = 3
