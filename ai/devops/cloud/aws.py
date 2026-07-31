"""AWS provider."""

from __future__ import annotations

from typing import Any


class AWSProvider:
    def __init__(self, region: str = "us-east-1") -> None:
        self._region = region
        self._resources: dict[str, dict[str, Any]] = {}

    def create_instance(self, name: str, instance_type: str = "t3.medium") -> dict[str, Any]:
        import uuid

        iid = str(uuid.uuid4())[:8]
        instance = {
            "instance_id": iid,
            "name": name,
            "type": instance_type,
            "region": self._region,
            "status": "running",
        }
        self._resources[iid] = instance
        return instance

    def create_s3_bucket(self, name: str) -> dict[str, Any]:
        bucket = {"name": name, "region": self._region, "versioning": True}
        self._resources[name] = bucket
        return bucket

    def list_resources(self) -> list[dict[str, Any]]:
        return list(self._resources.values())

    def terminate(self, resource_id: str) -> bool:
        if resource_id in self._resources:
            del self._resources[resource_id]
            return True
        return False

    def count(self) -> int:
        return len(self._resources)
