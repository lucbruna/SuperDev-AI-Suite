"""Digital Twin registry."""

from __future__ import annotations

import time
from typing import Any


class TwinRegistry:
    def __init__(self) -> None:
        self._twins: dict[str, dict[str, Any]] = {}

    def register(self, twin_id: str, name: str, twin_type: str = "enterprise", **kwargs: Any) -> dict[str, Any]:
        entry = {
            "twin_id": twin_id,
            "name": name,
            "type": twin_type,
            "status": "active",
            "registered_at": time.time(),
            **kwargs,
        }
        self._twins[twin_id] = entry
        return entry

    def unregister(self, twin_id: str) -> bool:
        if twin_id in self._twins:
            self._twins[twin_id]["status"] = "inactive"
            return True
        return False

    def get(self, twin_id: str) -> dict[str, Any] | None:
        return self._twins.get(twin_id)

    def list_active(self) -> list[dict[str, Any]]:
        return [t for t in self._twins.values() if t.get("status") == "active"]

    def list_by_type(self, twin_type: str) -> list[dict[str, Any]]:
        return [t for t in self._twins.values() if t.get("type") == twin_type]

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._twins.values())

    def count(self) -> int:
        return len(self._twins)

    def update(self, twin_id: str, **kwargs: Any) -> dict[str, Any] | None:
        t = self._twins.get(twin_id)
        if t:
            t.update(kwargs)
            return t
        return None
