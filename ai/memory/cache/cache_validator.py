from __future__ import annotations

from typing import Any


class CacheValidator:
    """Validates cache keys, values, and TTL parameters."""

    @staticmethod
    def validate_key(key: Any) -> bool:
        return isinstance(key, str) and len(key) > 0 and len(key) < 1024

    @staticmethod
    def validate_ttl(ttl: float) -> bool:
        return isinstance(ttl, (int, float)) and ttl > 0

    @staticmethod
    def validate_value(value: Any) -> bool:
        return value is not None

    @staticmethod
    def sanitize_key(key: str) -> str:
        return str(key).strip().replace(" ", "_")
