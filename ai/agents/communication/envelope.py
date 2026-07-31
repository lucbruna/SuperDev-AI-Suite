from __future__ import annotations

from typing import Any


class Envelope:
    """Message envelope with metadata wrapper."""

    def __init__(self, message: dict[str, Any], priority: int = 0, ttl: float = 300.0) -> None:
        self._message = message
        self._priority = priority
        self._ttl = ttl
        self._headers: dict[str, str] = {}

    @property
    def message(self) -> dict[str, Any]:
        return dict(self._message)

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def ttl(self) -> float:
        return self._ttl

    def set_header(self, key: str, value: str) -> None:
        self._headers[key] = value

    def get_header(self, key: str) -> str:
        return self._headers.get(key, "")

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": self._message,
            "priority": self._priority,
            "ttl": self._ttl,
            "headers": dict(self._headers),
        }
