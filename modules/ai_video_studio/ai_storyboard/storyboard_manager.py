"""Storyboard manager — lifecycle, storage and retrieval of storyboards."""
from __future__ import annotations

from typing import Any


class StoryboardManager:
    """Persists and manages storyboard assets in memory."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def save(self, name: str, storyboard: dict[str, Any]) -> str:
        storyboard["name"] = name
        storyboard.setdefault("version", 1)
        self._store[name] = storyboard
        return name

    def get(self, name: str) -> dict[str, Any] | None:
        return self._store.get(name)

    def list_names(self) -> list[str]:
        return list(self._store.keys())

    def delete(self, name: str) -> bool:
        return self._store.pop(name, None) is not None

    def bump_version(self, name: str) -> dict[str, Any] | None:
        sb = self._store.get(name)
        if sb is None:
            return None
        sb["version"] = sb.get("version", 1) + 1
        return sb

    def count(self) -> int:
        return len(self._store)


_storyboard_manager: StoryboardManager | None = None


def get_storyboard_manager() -> StoryboardManager:
    global _storyboard_manager
    if _storyboard_manager is None:
        _storyboard_manager = StoryboardManager()
    return _storyboard_manager
