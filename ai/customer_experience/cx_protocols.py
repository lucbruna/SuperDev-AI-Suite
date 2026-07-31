"""CX Protocols — Protocol definitions for customer experience."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CXProtocolType(Enum):
    REST = "rest"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    EVENT = "event"
    WEBHOOK = "webhook"


@dataclass
class CXProtocolConfig:
    name: str
    protocol_type: CXProtocolType = CXProtocolType.REST
    version: str = "1.0"
    base_url: str = ""
    auth_required: bool = True
    rate_limit: int = 1000
    settings: dict[str, Any] = field(default_factory=dict)


class CXProtocols:
    def __init__(self):
        self.protocols: dict[str, CXProtocolConfig] = {}

    def register(self, name: str, protocol_type: CXProtocolType = CXProtocolType.REST, **kwargs) -> CXProtocolConfig:
        config = CXProtocolConfig(name=name, protocol_type=protocol_type, **kwargs)
        self.protocols[name] = config
        return config

    def get(self, name: str) -> CXProtocolConfig | None:
        return self.protocols.get(name)

    def list_protocols(self) -> list[CXProtocolConfig]:
        return list(self.protocols.values())

    def deregister(self, name: str) -> bool:
        return self.protocols.pop(name, None) is not None

    def count(self) -> int:
        return len(self.protocols)
