"""
Connector Loader - Dynamic connector loading
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LoadedConnector:
    name: str
    module_path: str
    version: str = "1.0.0"
    loaded_at: datetime = field(default_factory=datetime.now)
    instance: Any = None


class ConnectorLoader:
    def __init__(self):
        self.loaded: Dict[str, LoadedConnector] = {}
        self.paths: List[str] = []

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

    def get_loaded(self, name: str) -> Optional[LoadedConnector]:
        return self.loaded.get(name)

    def is_loaded(self, name: str) -> bool:
        return name in self.loaded

    def list_loaded(self) -> List[LoadedConnector]:
        return list(self.loaded.values())

    def count(self) -> int:
        return len(self.loaded)
