"""
Connector Engine - Core connector logic
"""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConnectorType(Enum):
    REST_API = "rest_api"
    SOAP = "soap"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MESSAGE_QUEUE = "message_queue"
    FTP = "ftp"
    CLOUD = "cloud"
    ERP = "erp"
    CRM = "crm"
    CUSTOM = "custom"


class ConnectorState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ConnectorConfig:
    name: str
    connector_type: ConnectorType
    endpoint: str = ""
    credentials: dict[str, str] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)
    timeout: int = 30
    retries: int = 3


@dataclass
class ConnectorInstance:
    instance_id: str
    config: ConnectorConfig
    state: ConnectorState = ConnectorState.DISCONNECTED
    last_connected: datetime | None = None
    error_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ConnectorEngine:
    def __init__(self):
        self.connectors: dict[str, ConnectorInstance] = {}
        self.handlers: dict[str, Callable] = {}
        self.connection_pool: dict[str, Any] = {}

    def create_connector(self, config: ConnectorConfig) -> ConnectorInstance:
        instance_id = hashlib.sha256(f"{config.name}{config.connector_type.value}".encode()).hexdigest()[:16]
        instance = ConnectorInstance(instance_id=instance_id, config=config)
        self.connectors[instance_id] = instance
        return instance

    def connect(self, instance_id: str) -> bool:
        connector = self.connectors.get(instance_id)
        if not connector:
            return False
        connector.state = ConnectorState.CONNECTING
        handler = self.handlers.get(instance_id)
        if handler:
            try:
                handler("connect", connector.config)
                connector.state = ConnectorState.CONNECTED
                connector.last_connected = datetime.now()
                return True
            except Exception:
                connector.state = ConnectorState.ERROR
                connector.error_count += 1
                return False
        connector.state = ConnectorState.CONNECTED
        connector.last_connected = datetime.now()
        return True

    def disconnect(self, instance_id: str) -> bool:
        connector = self.connectors.get(instance_id)
        if connector:
            connector.state = ConnectorState.DISCONNECTED
            return True
        return False

    def register_handler(self, instance_id: str, handler: Callable) -> None:
        self.handlers[instance_id] = handler

    def get_connector(self, instance_id: str) -> ConnectorInstance | None:
        return self.connectors.get(instance_id)

    def list_connectors(self) -> list[ConnectorInstance]:
        return list(self.connectors.values())

    def get_connected(self) -> list[ConnectorInstance]:
        return [c for c in self.connectors.values() if c.state == ConnectorState.CONNECTED]

    def count(self) -> int:
        return len(self.connectors)
