"""Screenwriter manager — lifecycle and storage of scripts."""
from __future__ import annotations

from typing import Any


class ScreenwriterManager:
    """Persists and manages scripts in memory."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def save(self, name: str, script: dict[str, Any]) -> str:
        script["name"] = name
        script.setdefault("version", 1)
        self._store[name] = script
        return name

    def get(self, name: str) -> dict[str, Any] | None:
        return self._store.get(name)

    def list_names(self) -> list[str]:
        return list(self._store.keys())

    def delete(self, name: str) -> bool:
        return self._store.pop(name, None) is not None

    def count(self) -> int:
        return len(self._store)


_screenwriter_manager: ScreenwriterManager | None = None


def get_screenwriter_manager() -> ScreenwriterManager:
    global _screenwriter_manager
    if _screenwriter_manager is None:
        _screenwriter_manager = ScreenwriterManager()
    return _screenwriter_manager
