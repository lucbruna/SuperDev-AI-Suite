"""
Connector Manager - Lifecycle management
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ConnectorInfo:
    connector_id: str
    name: str
    connector_type: str
    status: str = "inactive"
    config: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime | None = None
    use_count: int = 0


class ConnectorManager:
    def __init__(self):
        self.connectors: dict[str, ConnectorInfo] = {}
        self.groups: dict[str, list[str]] = {}

    def register(self, name: str, connector_type: str, config: dict[str, Any] = None) -> ConnectorInfo:
        connector_id = hashlib.sha256(name.encode()).hexdigest()[:16]
        info = ConnectorInfo(connector_id=connector_id, name=name, connector_type=connector_type, config=config or {})
        self.connectors[connector_id] = info
        return info

    def unregister(self, connector_id: str) -> bool:
        if connector_id in self.connectors:
            del self.connectors[connector_id]
            return True
        return False

    def get_connector(self, connector_id: str) -> ConnectorInfo | None:
        return self.connectors.get(connector_id)

    def find_by_name(self, name: str) -> ConnectorInfo | None:
        for c in self.connectors.values():
            if c.name == name:
                return c
        return None

    def find_by_type(self, connector_type: str) -> list[ConnectorInfo]:
        return [c for c in self.connectors.values() if c.connector_type == connector_type]

    def create_group(self, name: str, connector_ids: list[str] = None) -> None:
        self.groups[name] = connector_ids or []

    def add_to_group(self, group_name: str, connector_id: str) -> bool:
        if group_name in self.groups:
            self.groups[group_name].append(connector_id)
            return True
        return False

    def get_group(self, group_name: str) -> list[ConnectorInfo]:
        ids = self.groups.get(group_name, [])
        return [self.connectors[i] for i in ids if i in self.connectors]

    def list_all(self) -> list[ConnectorInfo]:
        return list(self.connectors.values())

    def count(self) -> int:
        return len(self.connectors)
