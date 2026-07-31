"""Enterprise registry."""
from __future__ import annotations

import time
from typing import Any


class EnterpriseRegistry:
    def __init__(self) -> None:
        self._components: dict[str, dict[str, Any]] = {}
    def register(self, name: str, component_type: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {"name": name, "type": component_type, "metadata": metadata or {}, "registered_at": time.time(), "active": True}
        self._components[name] = entry
        return entry
    def unregister(self, name: str) -> bool:
        if name in self._components:
            self._components[name]["active"] = False
            return True
        return False
    def get(self, name: str) -> dict[str, Any] | None:
        return self._components.get(name)
    def list_active(self) -> list[str]:
        return [k for k, v in self._components.items() if v.get("active")]
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._components.values())
    def count(self) -> int:
        return len(self._components)
