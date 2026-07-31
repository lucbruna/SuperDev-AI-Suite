"""
Connector Registry - Connector discovery
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ConnectorDefinition:
    name: str
    connector_type: str
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    author: str = ""
    registered_at: datetime = field(default_factory=datetime.now)


class ConnectorRegistry:
    def __init__(self):
        self.definitions: dict[str, ConnectorDefinition] = {}
        self.categories: dict[str, list[str]] = {}

    def register(self, name: str, connector_type: str, description: str = "", capabilities: list[str] = None, **kwargs) -> ConnectorDefinition:
        definition = ConnectorDefinition(name=name, connector_type=connector_type, description=description, capabilities=capabilities or [], **kwargs)
        self.definitions[name] = definition
        self.categories.setdefault(connector_type, []).append(name)
        return definition

    def unregister(self, name: str) -> bool:
        if name in self.definitions:
            del self.definitions[name]
            return True
        return False

    def lookup(self, name: str) -> ConnectorDefinition | None:
        return self.definitions.get(name)

    def search(self, query: str) -> list[ConnectorDefinition]:
        return [d for d in self.definitions.values() if query.lower() in d.name.lower() or query.lower() in d.description.lower()]

    def get_by_type(self, connector_type: str) -> list[ConnectorDefinition]:
        names = self.categories.get(connector_type, [])
        return [self.definitions[n] for n in names if n in self.definitions]

    def list_all(self) -> list[ConnectorDefinition]:
        return list(self.definitions.values())

    def count(self) -> int:
        return len(self.definitions)
