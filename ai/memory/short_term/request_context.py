from __future__ import annotations

from typing import Any, Dict, Optional


class RequestContext:
    """Per-request context for isolating operation data."""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._headers: Dict[str, str] = {}
        self._params: Dict[str, str] = {}

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

    def set_data(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set_header(self, key: str, value: str) -> None:
        self._headers[key] = value

    def get_header(self, key: str, default: str = "") -> str:
        return self._headers.get(key, default)

    def set_param(self, key: str, value: str) -> None:
        self._params[key] = value

    def get_param(self, key: str, default: str = "") -> str:
        return self._params.get(key, default)

    def clear(self) -> None:
        self._data.clear()
        self._headers.clear()
        self._params.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": dict(self._data),
            "headers": dict(self._headers),
            "params": dict(self._params),
        }
