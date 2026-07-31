"""Data Platform Context — Context management for data platform operations."""

from datetime import datetime
from typing import Any


class DataPlatformContext:
    def __init__(self):
        self._context: dict[str, Any] = {}
        self._created_at = datetime.now()

    def set(self, key: str, value: Any) -> None:
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    def delete(self, key: str) -> bool:
        if key in self._context:
            del self._context[key]
            return True
        return False

    def has(self, key: str) -> bool:
        return key in self._context

    def clear(self) -> None:
        self._context.clear()

    def keys(self):
        return self._context.keys()

    def values(self):
        return self._context.values()

    def items(self):
        return self._context.items()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._context)

    @property
    def created_at(self) -> datetime:
        return self._created_at
