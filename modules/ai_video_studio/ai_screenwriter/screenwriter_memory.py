"""Screenwriter memory — stores past scripts and learned preferences."""
from __future__ import annotations

from typing import Any


class ScreenwriterMemory:
    """Remembers past scripts and tone preferences."""

    def __init__(self) -> None:
        self._scripts: list[dict[str, Any]] = []
        self._preferences: dict[str, Any] = {}

    def remember(self, script: dict[str, Any]) -> None:
        self._scripts.append(script)

    def set_preference(self, key: str, value: Any) -> None:
        self._preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self._preferences.get(key, default)

    def recent(self, limit: int = 5) -> list[dict[str, Any]]:
        return self._scripts[-limit:]

    def size(self) -> int:
        return len(self._scripts)


_screenwriter_memory: ScreenwriterMemory | None = None


def get_screenwriter_memory() -> ScreenwriterMemory:
    global _screenwriter_memory
    if _screenwriter_memory is None:
        _screenwriter_memory = ScreenwriterMemory()
    return _screenwriter_memory
