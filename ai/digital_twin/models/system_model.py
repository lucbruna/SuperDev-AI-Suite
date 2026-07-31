"""System model."""
from __future__ import annotations
from typing import Any, Dict, List
import time, uuid

class SystemModel:
    def __init__(self) -> None:
        self._systems: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, components: List[Dict[str, Any]], connections: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        system_id = str(uuid.uuid4())[:8]
        system = {"system_id": system_id, "name": name, "components": components, "connections": connections or [], "status": "created", "created_at": time.time()}
        self._systems[system_id] = system
        return system
    def get(self, system_id: str) -> Dict[str, Any]:
        return self._systems.get(system_id, {"error": "not_found"})
    def add_component(self, system_id: str, component: Dict[str, Any]) -> bool:
        if system_id not in self._systems:
            return False
        self._systems[system_id]["components"].append(component)
        return True
    def add_connection(self, system_id: str, source: str, target: str, relation: str = "connects_to") -> bool:
        if system_id not in self._systems:
            return False
        self._systems[system_id]["connections"].append({"source": source, "target": target, "relation": relation})
        return True
    def get_component(self, system_id: str, component_id: str) -> Dict[str, Any]:
        system = self._systems.get(system_id, {})
        for c in system.get("components", []):
            if c.get("id") == component_id:
                return c
        return {"error": "not_found"}
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._systems.values())
    def count(self) -> int:
        return len(self._systems)
