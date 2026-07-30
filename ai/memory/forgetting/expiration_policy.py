from __future__ import annotations

import time
from typing import Any, Dict, List


class ExpirationPolicy:
    """Manages expiration of memory entries based on TTL or age."""

    def __init__(self):
        self._policies: Dict[str, float] = {}

    def set_ttl(self, key: str, ttl_seconds: float) -> None:
        self._policies[key] = ttl_seconds

    def get_ttl(self, key: str) -> float | None:
        return self._policies.get(key)

    def remove_ttl(self, key: str) -> bool:
        return self._policies.pop(key, None) is not None

    def is_expired(self, key: str, entry: Dict[str, Any]) -> bool:
        ttl = self._policies.get(key)
        if ttl is None:
            return False
        created = entry.get("created_at", entry.get("timestamp", time.time()))
        return time.time() - created >= ttl

    def find_expired(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in entries.items() if self.is_expired(k, v)}

    def expired_count(self, entries: Dict[str, Any]) -> int:
        return len(self.find_expired(entries))

    def clear(self) -> None:
        self._policies.clear()
