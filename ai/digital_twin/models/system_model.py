"""System model."""

from __future__ import annotations

import time
import uuid
from typing import Any


class SystemModel:
    def __init__(self) -> None:
        self._systems: dict[str, dict[str, Any]] = {}

    def create(
        self, name: str, components: list[dict[str, Any]], connections: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        system_id = str(uuid.uuid4())[:8]
        system = {
            "system_id": system_id,
            "name": name,
            "components": components,
            "connections": connections or [],
            "status": "created",
            "created_at": time.time(),
        }
        self._systems[system_id] = system
        return system

    def get(self, system_id: str) -> dict[str, Any]:
        return self._systems.get(system_id, {"error": "not_found"})

    def add_component(self, system_id: str, component: dict[str, Any]) -> bool:
        if system_id not in self._systems:
            return False
        self._systems[system_id]["components"].append(component)
        return True

    def add_connection(self, system_id: str, source: str, target: str, relation: str = "connects_to") -> bool:
        if system_id not in self._systems:
            return False
        self._systems[system_id]["connections"].append({"source": source, "target": target, "relation": relation})
        return True

    def get_component(self, system_id: str, component_id: str) -> dict[str, Any]:
        system = self._systems.get(system_id, {})
        for c in system.get("components", []):
            if c.get("id") == component_id:
                return c
        return {"error": "not_found"}

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._systems.values())

    def count(self) -> int:
        return len(self._systems)
