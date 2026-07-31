"""Resource manager."""

from __future__ import annotations

from typing import Any


class ResourceManager:
    def __init__(self) -> None:
        self._resources: dict[str, dict[str, Any]] = {}

    def add(self, name: str, resource_type: str, specs: dict[str, Any] = None) -> dict[str, Any]:
        resource = {"name": name, "type": resource_type, "specs": specs or {}, "status": "available"}
        self._resources[name] = resource
        return resource

    def get(self, name: str) -> dict[str, Any]:
        return self._resources.get(name, {"error": "not_found"})

    def allocate(self, name: str, purpose: str) -> dict[str, Any]:
        if name not in self._resources:
            return {"error": "not_found"}
        self._resources[name]["status"] = "allocated"
        self._resources[name]["purpose"] = purpose
        return self._resources[name]

    def release(self, name: str) -> bool:
        if name in self._resources:
            self._resources[name]["status"] = "available"
            self._resources[name].pop("purpose", None)
            return True
        return False

    def list_available(self) -> list[dict[str, Any]]:
        return [r for r in self._resources.values() if r["status"] == "available"]

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._resources.values())

    def count(self) -> int:
        return len(self._resources)
