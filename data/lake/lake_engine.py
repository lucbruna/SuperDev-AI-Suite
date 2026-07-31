from __future__ import annotations

import hashlib
from typing import Any

from ..data_models import DataFormat, LakeObject


class LakeEngine:
    """Data Lake — raw/processed/curated zones, metadata, lifecycle."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.lake
        self._zones: dict[str, dict[str, LakeObject]] = {
            zone: {} for zone in self.config.zones
        }
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def ensure_zone(self, zone: str) -> None:
        self._zones.setdefault(zone, {})

    def put(
        self,
        zone: str,
        key: str,
        data: bytes,
        data_format: DataFormat = DataFormat.JSON,
        metadata: dict[str, Any] | None = None,
    ) -> LakeObject:
        self.ensure_zone(zone)
        obj = LakeObject(
            path=f"{zone}/{key}",
            zone=zone,
            format=data_format,
            size_bytes=len(data),
            checksum=hashlib.sha256(data).hexdigest()[:16],
            metadata=metadata or {},
        )
        self._zones[zone][key] = obj
        self.engine.metrics.increment("lake.objects")
        return obj

    def get(self, zone: str, key: str) -> LakeObject | None:
        return self._zones.get(zone, {}).get(key)

    def list(self, zone: str) -> list[LakeObject]:
        return list(self._zones.get(zone, {}).values())

    def promote(self, key: str, from_zone: str, to_zone: str) -> LakeObject | None:
        """Move an object from one zone to another (raw → processed → curated)."""
        obj = self.get(from_zone, key)
        if obj is None:
            return None
        self._zones.get(from_zone, {}).pop(key, None)
        promoted = LakeObject(
            object_id=obj.object_id,
            path=f"{to_zone}/{key}",
            zone=to_zone,
            format=obj.format,
            size_bytes=obj.size_bytes,
            checksum=obj.checksum,
            metadata=dict(obj.metadata, promoted_from=from_zone),
            uploaded_at=obj.uploaded_at,
        )
        self.ensure_zone(to_zone)
        self._zones[to_zone][key] = promoted
        return promoted

    def lifecycle_sweep(self, max_objects_per_zone: int = 1000) -> dict[str, int]:
        """Enforce lifecycle limits across zones."""
        removed = 0
        for zone, objects in self._zones.items():
            while len(objects) > max_objects_per_zone:
                oldest_key = min(objects, key=lambda k: objects[k].uploaded_at)
                del objects[oldest_key]
                removed += 1
        return {"removed": removed}

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "zones": {zone: len(objects) for zone, objects in self._zones.items()},
        }


__all__ = ["LakeEngine"]
