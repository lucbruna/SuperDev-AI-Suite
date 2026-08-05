"""AIOS Storage Service — namespaced key/value storage.

In-memory backend by default; the interface matches what a durable
backend (S3, DB) would expose for module state.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class StorageService:
    """Namespaced key/value store with in-memory backend."""

    def __init__(self) -> None:
        self._buckets: dict[str, dict[str, dict[str, Any]]] = {}

    def put(self, bucket: str, key: str, value: Any, **meta: Any) -> dict[str, Any]:
        store = self._buckets.setdefault(bucket, {})
        item = {
            "key": key,
            "value": value,
            "etag": f"et-{uuid.uuid4().hex[:10]}",
            "timestamp": time.time(),
            "meta": meta,
        }
        store[key] = item
        return item

    def get(self, bucket: str, key: str, default: Any = None) -> Any:
        item = self._buckets.get(bucket, {}).get(key)
        if item is None:
            return default
        return item["value"]

    def get_item(self, bucket: str, key: str) -> dict[str, Any] | None:
        return self._buckets.get(bucket, {}).get(key)

    def delete(self, bucket: str, key: str) -> bool:
        return self._buckets.get(bucket, {}).pop(key, None) is not None

    def list_keys(self, bucket: str) -> list[str]:
        return sorted(self._buckets.get(bucket, {}))

    def clear_bucket(self, bucket: str) -> None:
        self._buckets.pop(bucket, None)

    def buckets(self) -> list[str]:
        return sorted(self._buckets)

    def snapshot(self) -> dict[str, Any]:
        return {
            "buckets": self.buckets(),
            "object_count": sum(len(b) for b in self._buckets.values()),
        }
