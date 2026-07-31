from __future__ import annotations

import json
from typing import Any


class CacheSerializer:
    """Serializes cache entries to/from JSON-compatible format."""

    @staticmethod
    def serialize(value: Any) -> str:
        return json.dumps(value, default=str)

    @staticmethod
    def deserialize(data: str) -> Any:
        return json.loads(data)

    @staticmethod
    def serialize_entry(key: str, value: Any, ttl: float) -> dict[str, Any]:
        return {"key": key, "value": value, "ttl": ttl}

    @staticmethod
    def deserialize_entry(data: dict[str, Any]) -> dict[str, Any]:
        return data
