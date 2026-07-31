"""
Connector Registry - Connector discovery
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConnectorDefinition:
    name: str
    connector_type: str
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    author: str = ""
    registered_at: datetime = field(default_factory=datetime.now)


class ConnectorRegistry:
    def __init__(self):
        self.definitions: Dict[str, ConnectorDefinition] = {}
        self.categories: Dict[str, List[str]] = {}

    def register(self, name: str, connector_type: str, description: str = "", capabilities: List[str] = None, **kwargs) -> ConnectorDefinition:
        definition = ConnectorDefinition(name=name, connector_type=connector_type, description=description, capabilities=capabilities or [], **kwargs)
        self.definitions[name] = definition
        self.categories.setdefault(connector_type, []).append(name)
        return definition

    def unregister(self, name: str) -> bool:
        if name in self.definitions:
            del self.definitions[name]
            return True
        return False

    def lookup(self, name: str) -> Optional[ConnectorDefinition]:
        return self.definitions.get(name)

    def search(self, query: str) -> List[ConnectorDefinition]:
        return [d for d in self.definitions.values() if query.lower() in d.name.lower() or query.lower() in d.description.lower()]

    def get_by_type(self, connector_type: str) -> List[ConnectorDefinition]:
        names = self.categories.get(connector_type, [])
        return [self.definitions[n] for n in names if n in self.definitions]

    def list_all(self) -> List[ConnectorDefinition]:
        return list(self.definitions.values())

    def count(self) -> int:
        return len(self.definitions)
