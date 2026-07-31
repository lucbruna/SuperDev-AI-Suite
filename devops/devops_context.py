from __future__ import annotations

from typing import Any


class DevOpsContext:
    """Context holder for current DevOps operation scope."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def clear(self) -> None:
        self._data.clear()

    @property
    def environment(self) -> str:
        return self._data.get("environment", "development")

    @environment.setter
    def environment(self, value: str) -> None:
        self._data["environment"] = value
