"""BI Protocols — Protocol definitions for BI operations."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List


class BIProtocolType(Enum):
    REST = "rest"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    EVENT = "event"


@dataclass
class BIProtocolConfig:
    name: str
    protocol_type: BIProtocolType = BIProtocolType.REST
    version: str = "1.0"
    base_url: str = ""
    auth_required: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


class BIProtocols:
    def __init__(self):
        self.protocols: Dict[str, BIProtocolConfig] = {}

    def register(self, name: str, protocol_type: BIProtocolType = BIProtocolType.REST, **kwargs) -> BIProtocolConfig:
        config = BIProtocolConfig(name=name, protocol_type=protocol_type, **kwargs)
        self.protocols[name] = config
        return config

    def get(self, name: str) -> BIProtocolConfig | None:
        return self.protocols.get(name)

    def list_protocols(self) -> List[BIProtocolConfig]:
        return list(self.protocols.values())

    def count(self) -> int:
        return len(self.protocols)
