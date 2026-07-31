"""Identity history tracking."""

from __future__ import annotations

import time
import uuid
from typing import Any


class IdentityHistory:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def record(self, user_id: str, action: str, details: dict[str, Any]) -> None:
        self._entries.append(
            {
                "id": str(uuid.uuid4())[:8],
                "user_id": user_id,
                "action": action,
                "details": details,
                "timestamp": time.time(),
            }
        )

    def get(self, user_id: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        entries = [e for e in self._entries if user_id is None or e["user_id"] == user_id]
        return entries[-limit:]

    def count(self) -> int:
        return len(self._entries)
