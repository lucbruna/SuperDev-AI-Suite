"""Database health checks."""
from __future__ import annotations
from typing import Any, Dict, List

class DatabaseCheck:
    def __init__(self) -> None:
        self._connections: Dict[str, Dict[str, Any]] = {}
    def register(self, name: str, config: Dict[str, Any]) -> None:
        self._connections[name] = config
    def check(self, name: str) -> Dict[str, Any]:
        config = self._connections.get(name)
        if not config:
            return {"database": name, "status": "not_configured"}
        return {"database": name, "status": "healthy", "type": config.get("type", "unknown")}
    def check_all(self) -> List[Dict[str, Any]]:
        return [self.check(name) for name in self._connections]
    def list_databases(self) -> List[str]:
        return list(self._connections.keys())
    def remove(self, name: str) -> bool:
        if name in self._connections:
            del self._connections[name]
            return True
        return False
