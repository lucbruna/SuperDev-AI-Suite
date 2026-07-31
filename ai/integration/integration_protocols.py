"""
Integration Protocols - Protocol definitions
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProtocolType(Enum):
    REST = "rest"
    SOAP = "soap"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MQTT = "mqtt"
    AMQP = "amqp"
    KAFKA = "kafka"
    FTP = "ftp"
    SFTP = "sftp"


@dataclass
class ProtocolConfig:
    protocol_type: ProtocolType
    version: str = ""
    transport: str = "https"
    encoding: str = "utf-8"
    compression: str = "none"
    timeout: int = 30
    retries: int = 3
    settings: dict[str, Any] = field(default_factory=dict)


class IntegrationProtocols:
    def __init__(self):
        self.protocols: dict[str, ProtocolConfig] = {}
        self.protocol_handlers: dict[str, Any] = {}

    def register_protocol(self, name: str, protocol_type: ProtocolType, **kwargs) -> ProtocolConfig:
        config = ProtocolConfig(protocol_type=protocol_type, **kwargs)
        self.protocols[name] = config
        return config

    def get_protocol(self, name: str) -> ProtocolConfig | None:
        return self.protocols.get(name)

    def register_handler(self, protocol_name: str, handler: Any) -> None:
        self.protocol_handlers[protocol_name] = handler

    def get_handler(self, protocol_name: str) -> Any | None:
        return self.protocol_handlers.get(protocol_name)

    def list_protocols(self) -> list[ProtocolConfig]:
        return list(self.protocols.values())

    def get_by_type(self, protocol_type: ProtocolType) -> list[ProtocolConfig]:
        return [p for p in self.protocols.values() if p.protocol_type == protocol_type]

    def count(self) -> int:
        return len(self.protocols)
