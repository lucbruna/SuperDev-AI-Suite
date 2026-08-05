"""Avatar history — record of generated presenter outputs."""
from __future__ import annotations

import time
from typing import Any


class AvatarHistory:
    """Bounded history of presenter generation results."""

    def __init__(self, limit: int = 100) -> None:
        self.limit = max(1, limit)
        self._entries: list[dict[str, Any]] = []

    def push(self, result: dict[str, Any]) -> None:
        entry = {
            "ts": round(time.time(), 3),
            "id": result.get("id"),
            "actor": result.get("actor", {}).get("id") if isinstance(result.get("actor"), dict) else result.get("actor"),
            "scene_type": result.get("scene_type"),
            "expression": result.get("expression"),
            "duration": result.get("duration"),
            "output_path": result.get("output_path"),
        }
        self._entries.append(entry)
        if len(self._entries) > self.limit:
            self._entries.pop(0)

    def list(self, limit: int | None = None) -> list[dict[str, Any]]:
        entries = self._entries
        if limit is not None:
            entries = entries[-limit:]
        return list(entries)

    def clear(self) -> None:
        self._entries.clear()


_avatar_history: AvatarHistory | None = None


def get_avatar_history() -> AvatarHistory:
    global _avatar_history
    if _avatar_history is None:
        _avatar_history = AvatarHistory()
    return _avatar_history
