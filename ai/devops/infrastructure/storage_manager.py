"""Storage manager."""
from __future__ import annotations

from typing import Any


class StorageManager:
    def __init__(self) -> None:
        self._volumes: dict[str, dict[str, Any]] = {}
        self._buckets: dict[str, dict[str, Any]] = {}
    def create_volume(self, name: str, size_gb: int = 100, volume_type: str = "ssd") -> dict[str, Any]:
        volume = {"name": name, "size_gb": size_gb, "type": volume_type, "status": "available", "used_gb": 0}
        self._volumes[name] = volume
        return volume
    def attach_volume(self, name: str, server_id: str) -> bool:
        if name not in self._volumes:
            return False
        self._volumes[name]["status"] = "attached"
        self._volumes[name]["server_id"] = server_id
        return True
    def detach_volume(self, name: str) -> bool:
        if name in self._volumes:
            self._volumes[name]["status"] = "available"
            self._volumes[name].pop("server_id", None)
            return True
        return False
    def create_bucket(self, name: str, region: str = "us-east-1") -> dict[str, Any]:
        bucket = {"name": name, "region": region, "objects": 0, "size_bytes": 0}
        self._buckets[name] = bucket
        return bucket
    def get_volume(self, name: str) -> dict[str, Any]:
        return self._volumes.get(name, {"error": "not_found"})
    def get_bucket(self, name: str) -> dict[str, Any]:
        return self._buckets.get(name, {"error": "not_found"})
    def list_volumes(self) -> list[dict[str, Any]]:
        return list(self._volumes.values())
    def list_buckets(self) -> list[dict[str, Any]]:
        return list(self._buckets.values())
    def count(self) -> int:
        return len(self._volumes) + len(self._buckets)
