"""Factory Protocols - Protocol definitions for factory operations."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class ProtocolType(Enum):
    REST = "rest"
    GRPC = "grpc"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    CLI = "cli"


@dataclass
class ProtocolConfig:
    name: str
    protocol_type: ProtocolType = ProtocolType.REST
    version: str = "1.0"
    base_url: str = ""
    auth_required: bool = True
    rate_limit: int = 1000
    settings: Dict[str, Any] = field(default_factory=dict)


class FactoryProtocols:
    def __init__(self):
        self.protocols: Dict[str, ProtocolConfig] = {}

    def register(self, name: str, protocol_type: ProtocolType = ProtocolType.REST, **kwargs) -> ProtocolConfig:
        config = ProtocolConfig(name=name, protocol_type=protocol_type, **kwargs)
        self.protocols[name] = config
        return config

    def get(self, name: str) -> Optional[ProtocolConfig]:
        return self.protocols.get(name)

    def list_protocols(self) -> List[ProtocolConfig]:
        return list(self.protocols.values())

    def count(self) -> int:
        return len(self.protocols)
