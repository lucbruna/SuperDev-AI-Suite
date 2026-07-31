"""DevOps registry."""
from __future__ import annotations

import time
from typing import Any


class DevOpsRegistry:
    def __init__(self) -> None:
        self._resources: dict[str, dict[str, Any]] = {}
    def register(self, resource_id: str, name: str, resource_type: str = "server", **kwargs: Any) -> dict[str, Any]:
        entry = {"resource_id": resource_id, "name": name, "type": resource_type, "status": "active", "registered_at": time.time(), **kwargs}
        self._resources[resource_id] = entry
        return entry
    def unregister(self, resource_id: str) -> bool:
        if resource_id in self._resources:
            self._resources[resource_id]["status"] = "inactive"
            return True
        return False
    def get(self, resource_id: str) -> dict[str, Any] | None:
        return self._resources.get(resource_id)
    def list_active(self) -> list[dict[str, Any]]:
        return [r for r in self._resources.values() if r.get("status") == "active"]
    def list_by_type(self, resource_type: str) -> list[dict[str, Any]]:
        return [r for r in self._resources.values() if r.get("type") == resource_type]
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._resources.values())
    def count(self) -> int:
        return len(self._resources)
