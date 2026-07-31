"""Monitoring component registry."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MonitoringRegistry:
    def __init__(self) -> None:
        self._components: Dict[str, Dict[str, Any]] = {}
        self._health_cache: Dict[str, Dict[str, Any]] = {}
    def register(self, name: str, component_type: str = "", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        entry = {"name": name, "type": component_type, "metadata": metadata or {}, "registered_at": time.time(), "active": True}
        self._components[name] = entry
        return entry
    def unregister(self, name: str) -> bool:
        if name in self._components:
            self._components[name]["active"] = False
            return True
        return False
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self._components.get(name)
    def update_health(self, name: str, status: str, details: str = "") -> None:
        self._health_cache[name] = {"status": status, "details": details, "timestamp": time.time()}
    def get_health(self, name: str) -> Optional[Dict[str, Any]]:
        return self._health_cache.get(name)
    def list_active(self) -> List[str]:
        return [k for k, v in self._components.items() if v.get("active")]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._components.values())
    def count(self) -> int:
        return len(self._components)
