from __future__ import annotations

import time
from typing import Any


class WebSocketConnection:
    """Represents a single WebSocket connection."""

    def __init__(
        self,
        connection_id: str,
        user_id: str = "",
        path: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._connection_id = connection_id
        self._path = path
        self._user_id = user_id
        self._metadata = metadata or {}
        self._connected_at = time.time()
        self._is_alive = True
        self._close_code: int | None = None
        self._close_reason: str = ""

    @property
    def connection_id(self) -> str:
        return self._connection_id

    @property
    def path(self) -> str:
        return self._path

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def connected_at(self) -> float:
        return self._connected_at

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    @property
    def close_code(self) -> int | None:
        return self._close_code

    @property
    def close_reason(self) -> str:
        return self._close_reason

    def mark_closed(self, code: int = 1000, reason: str = "") -> None:
        self._is_alive = False
        self._close_code = code
        self._close_reason = reason

    def update_metadata(self, **kwargs: Any) -> None:
        self._metadata.update(kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "connection_id": self._connection_id,
            "path": self._path,
            "user_id": self._user_id,
            "connected_at": self._connected_at,
            "is_alive": self._is_alive,
            "close_code": self._close_code,
            "close_reason": self._close_reason,
        }
