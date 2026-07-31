"""
Integration Protocols - Protocol definitions
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


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
    settings: Dict[str, Any] = field(default_factory=dict)


class IntegrationProtocols:
    def __init__(self):
        self.protocols: Dict[str, ProtocolConfig] = {}
        self.protocol_handlers: Dict[str, Any] = {}

    def register_protocol(self, name: str, protocol_type: ProtocolType, **kwargs) -> ProtocolConfig:
        config = ProtocolConfig(protocol_type=protocol_type, **kwargs)
        self.protocols[name] = config
        return config

    def get_protocol(self, name: str) -> Optional[ProtocolConfig]:
        return self.protocols.get(name)

    def register_handler(self, protocol_name: str, handler: Any) -> None:
        self.protocol_handlers[protocol_name] = handler

    def get_handler(self, protocol_name: str) -> Optional[Any]:
        return self.protocol_handlers.get(protocol_name)

    def list_protocols(self) -> List[ProtocolConfig]:
        return list(self.protocols.values())

    def get_by_type(self, protocol_type: ProtocolType) -> List[ProtocolConfig]:
        return [p for p in self.protocols.values() if p.protocol_type == protocol_type]

    def count(self) -> int:
        return len(self.protocols)
