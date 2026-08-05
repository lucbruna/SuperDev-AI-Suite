"""Cloud Storage — multi-provider object storage abstraction (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class CloudStorage:
    """Store and retrieve media objects across cloud providers."""

    def __init__(self) -> None:
        self._objects: dict[str, dict] = {}

    def put(self, *, key: str = "", size_mb: float = 0.0, provider: str = "default") -> dict:
        """Store an object (simulated in memory)."""
        key = key or "unnamed"
        self._objects[key] = {"key": key, "size_mb": size_mb, "provider": provider, "stored": True}
        return self._objects[key]

    def get(self, *, key: str = "") -> dict | None:
        """Retrieve an object reference."""
        return self._objects.get(key)

    def list(self) -> list[dict]:
        return list(self._objects.values())

    def delete(self, *, key: str = "") -> bool:
        return self._objects.pop(key, None) is not None

    def total_size_mb(self) -> float:
        return round(sum(obj.get("size_mb", 0.0) for obj in self._objects.values()), 2)

    def stats(self) -> dict[str, int | float]:
        return {"objects": len(self._objects), "total_size_mb": self.total_size_mb()}


_STORAGE: CloudStorage | None = None


def get_cloud_storage() -> CloudStorage:
    """Get the module-level singleton cloud storage."""
    global _STORAGE
    if _STORAGE is None:
        _STORAGE = CloudStorage()
    return _STORAGE
