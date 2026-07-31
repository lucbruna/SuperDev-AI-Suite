"""Azure provider."""
from __future__ import annotations

from typing import Any


class AzureProvider:
    def __init__(self, region: str = "eastus") -> None:
        self._region = region
        self._resources: dict[str, dict[str, Any]] = {}
    def create_vm(self, name: str, vm_size: str = "Standard_D2s_v3") -> dict[str, Any]:
        import uuid
        vid = str(uuid.uuid4())[:8]
        vm = {"vm_id": vid, "name": name, "size": vm_size, "region": self._region, "status": "running"}
        self._resources[vid] = vm
        return vm
    def create_storage_account(self, name: str) -> dict[str, Any]:
        account = {"name": name, "region": self._region, "sku": "Standard_LRS"}
        self._resources[name] = account
        return account
    def list_resources(self) -> list[dict[str, Any]]:
        return list(self._resources.values())
    def delete(self, resource_id: str) -> bool:
        if resource_id in self._resources:
            del self._resources[resource_id]
            return True
        return False
    def count(self) -> int:
        return len(self._resources)
