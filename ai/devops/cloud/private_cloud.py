"""Private cloud provider."""

from __future__ import annotations

from typing import Any


class PrivateCloudProvider:
    def __init__(self, datacenter: str = "dc-01") -> None:
        self._datacenter = datacenter
        self._resources: dict[str, dict[str, Any]] = {}

    def create_vm(self, name: str, cpu: int = 4, memory_gb: int = 16) -> dict[str, Any]:
        vm = {"name": name, "cpu": cpu, "memory_gb": memory_gb, "datacenter": self._datacenter, "status": "running"}
        self._resources[name] = vm
        return vm

    def list_resources(self) -> list[dict[str, Any]]:
        return list(self._resources.values())

    def delete(self, name: str) -> bool:
        if name in self._resources:
            del self._resources[name]
            return True
        return False

    def count(self) -> int:
        return len(self._resources)
