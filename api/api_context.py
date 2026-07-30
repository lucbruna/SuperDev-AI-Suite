from __future__ import annotations

import time
from typing import Any

from .api_models import APIRequest


class APIContext:
    """Request-scoped context for the API layer."""

    def __init__(self, request: APIRequest | None = None) -> None:
        self._request = request
        self._start_time = time.time()
        self._attributes: dict[str, Any] = {}
        self._user: dict[str, Any] | None = None

    @property
    def request(self) -> APIRequest | None:
        return self._request

    @property
    def user(self) -> dict[str, Any] | None:
        return self._user

    @user.setter
    def user(self, value: dict[str, Any] | None) -> None:
        self._user = value

    def set(self, key: str, value: Any) -> None:
        self._attributes[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)

    @property
    def elapsed_ms(self) -> float:
        return (time.time() - self._start_time) * 1000

    @property
    def request_id(self) -> str:
        return self._request.request_id if self._request else ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "attributes": dict(self._attributes),
            "has_user": self._user is not None,
        }
