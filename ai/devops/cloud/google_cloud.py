"""Google Cloud provider."""
from __future__ import annotations

from typing import Any


class GoogleCloudProvider:
    def __init__(self, region: str = "us-central1") -> None:
        self._region = region
        self._resources: dict[str, dict[str, Any]] = {}
    def create_instance(self, name: str, machine_type: str = "e2-medium") -> dict[str, Any]:
        import uuid
        iid = str(uuid.uuid4())[:8]
        instance = {"instance_id": iid, "name": name, "machine_type": machine_type, "region": self._region, "status": "running"}
        self._resources[iid] = instance
        return instance
    def create_bucket(self, name: str) -> dict[str, Any]:
        bucket = {"name": name, "region": self._region, "storage_class": "STANDARD"}
        self._resources[name] = bucket
        return bucket
    def list_resources(self) -> list[dict[str, Any]]:
        return list(self._resources.values())
    def delete(self, resource_id: str) -> bool:
        if resource_id in self._resources:
            del self._resources[resource_id]
            return True
        return False
    def count(self) -> int:
        return len(self._resources)
