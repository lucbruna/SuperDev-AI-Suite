"""ERP Protocols — Protocol definitions for ERP operations."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List


class ERPProtocolType(Enum):
    REST = "rest"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    EVENT = "event"
    WEBHOOK = "webhook"


@dataclass
class ERPProtocolConfig:
    name: str
    protocol_type: ERPProtocolType = ERPProtocolType.REST
    version: str = "1.0"
    base_url: str = ""
    auth_required: bool = True
    rate_limit: int = 1000
    settings: Dict[str, Any] = field(default_factory=dict)


class ERPProtocols:
    def __init__(self):
        self.protocols: Dict[str, ERPProtocolConfig] = {}

    def register(self, name: str, protocol_type: ERPProtocolType = ERPProtocolType.REST, **kwargs) -> ERPProtocolConfig:
        config = ERPProtocolConfig(name=name, protocol_type=protocol_type, **kwargs)
        self.protocols[name] = config
        return config

    def get(self, name: str) -> ERPProtocolConfig | None:
        return self.protocols.get(name)

    def list_protocols(self) -> List[ERPProtocolConfig]:
        return list(self.protocols.values())

    def deregister(self, name: str) -> bool:
        return self.protocols.pop(name, None) is not None

    def count(self) -> int:
        return len(self.protocols)
