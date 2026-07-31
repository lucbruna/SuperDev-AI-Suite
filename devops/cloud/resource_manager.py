from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cloud_engine import CloudEngine


class ResourceManager:
    """Manages cloud resources across providers (in-memory)."""

    def __init__(self, engine: CloudEngine) -> None:
        self._log = logging.getLogger("superdev.devops.cloud.resources")
        self._engine = engine
        self._resources: dict[str, dict[str, Any]] = {}

    def create(self, provider: str, resource_type: str, name: str, **kwargs: Any) -> dict[str, Any]:
        """Create a resource, returning a dict with the resource_id."""
        resource_id = f"{provider}-{resource_type}-{uuid.uuid4().hex[:6]}"
        record: dict[str, Any] = {
            "resource_id": resource_id,
            "provider": provider,
            "resource_type": resource_type,
            "name": name,
            "status": "running",
            "created_at": time.time(),
            "tags": dict(kwargs.get("tags", {})),
        }
        record.update({k: v for k, v in kwargs.items() if k != "tags"})
        self._resources[resource_id] = record
        self._log.info("cloud resource %s (%s/%s) created", resource_id, provider, resource_type)
        return dict(record)

    def delete(self, provider: str, resource_id: str) -> bool:
        record = self._resources.get(resource_id)
        if record is None or record.get("provider") != provider:
            return False
        record["status"] = "terminated"
        return True

    def list(self, provider: str | None = None) -> list[dict[str, Any]]:
        records = list(self._resources.values())
        if provider is not None:
            records = [r for r in records if r["provider"] == provider]
        return [dict(r) for r in records]

    def get(self, provider: str, resource_id: str) -> dict[str, Any]:
        record = self._resources.get(resource_id)
        if record is None or record.get("provider") != provider:
            raise KeyError(f"resource not found: {resource_id}")
        return dict(record)

    def tag(self, provider: str, resource_id: str, tags: dict[str, str]) -> bool:
        record = self._resources.get(resource_id)
        if record is None or record.get("provider") != provider:
            return False
        record.setdefault("tags", {}).update(tags)
        return True
