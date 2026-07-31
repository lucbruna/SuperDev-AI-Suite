"""Resource monitor."""

from __future__ import annotations

from typing import Any


class ResourceMonitor:
    def __init__(self) -> None:
        self._resources: dict[str, dict[str, Any]] = {}

    def register(self, name: str, resource_type: str) -> dict[str, Any]:
        resource = {"name": name, "type": resource_type, "cpu": 0, "memory": 0, "disk": 0, "status": "healthy"}
        self._resources[name] = resource
        return resource

    def update_metrics(self, name: str, cpu: float, memory: float, disk: float) -> bool:
        if name not in self._resources:
            return False
        self._resources[name]["cpu"] = cpu
        self._resources[name]["memory"] = memory
        self._resources[name]["disk"] = disk
        if cpu > 90 or memory > 90:
            self._resources[name]["status"] = "critical"
        elif cpu > 70 or memory > 70:
            self._resources[name]["status"] = "warning"
        else:
            self._resources[name]["status"] = "healthy"
        return True

    def get_status(self, name: str) -> dict[str, Any]:
        return self._resources.get(name, {"error": "not_found"})

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._resources.values())

    def list_unhealthy(self) -> list[dict[str, Any]]:
        return [r for r in self._resources.values() if r["status"] != "healthy"]

    def count(self) -> int:
        return len(self._resources)
