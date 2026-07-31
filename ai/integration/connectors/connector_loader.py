"""
Connector Loader - Dynamic connector loading
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LoadedConnector:
    name: str
    module_path: str
    version: str = "1.0.0"
    loaded_at: datetime = field(default_factory=datetime.now)
    instance: Any = None


class ConnectorLoader:
    def __init__(self):
        self.loaded: dict[str, LoadedConnector] = {}
        self.paths: list[str] = []

    def register_path(self, path: str) -> None:
        if path not in self.paths:
            self.paths.append(path)

    def load(self, name: str, module_path: str) -> LoadedConnector:
        connector = LoadedConnector(name=name, module_path=module_path)
        self.loaded[name] = connector
        return connector

    def unload(self, name: str) -> bool:
        if name in self.loaded:
            del self.loaded[name]
            return True
        return False

    def get_loaded(self, name: str) -> LoadedConnector | None:
        return self.loaded.get(name)

    def is_loaded(self, name: str) -> bool:
        return name in self.loaded

    def list_loaded(self) -> list[LoadedConnector]:
        return list(self.loaded.values())

    def count(self) -> int:
        return len(self.loaded)
