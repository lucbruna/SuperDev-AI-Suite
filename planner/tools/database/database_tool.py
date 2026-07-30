from __future__ import annotations

from typing import Any


class DatabaseTool:
    """Base class for database adapters."""

    def __init__(self, connection_string: str = ""):
        self.connection_string = connection_string
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def execute(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return []

    def execute_many(self, query: str, params_list: list[dict[str, Any]]) -> int:
        return 0
