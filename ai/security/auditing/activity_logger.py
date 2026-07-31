"""Activity logging."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any


class ActivityLogger:
    def __init__(self) -> None:
        self._logs: list[dict[str, Any]] = []
        self._buffers: dict[str, list[dict[str, Any]]] = {}

    def log(self, category: str, action: str, user_id: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = {
            "log_id": str(uuid.uuid4())[:8],
            "category": category,
            "action": action,
            "user_id": user_id,
            "details": details or {},
            "timestamp": time.time(),
        }
        self._logs.append(entry)
        self._buffers.setdefault(category, []).append(entry)
        return entry

    def get_by_category(self, category: str, limit: int = 100) -> list[dict[str, Any]]:
        return self._buffers.get(category, [])[-limit:]

    def get_by_user(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        return [e for e in self._logs if e["user_id"] == user_id][-limit:]

    def get_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._logs[-limit:]

    def search(self, keyword: str) -> list[dict[str, Any]]:
        return [e for e in self._logs if keyword.lower() in json.dumps(e, default=str).lower()]

    def clear_category(self, category: str) -> int:
        n = len(self._buffers.get(category, []))
        self._buffers.pop(category, None)
        return n

    def count(self) -> int:
        return len(self._logs)
