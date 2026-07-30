from __future__ import annotations

from typing import Any, Dict, Optional


class SessionMemory:
    """Session-scoped memory for active conversation or workflow."""

    def __init__(self, session_id: str = ""):
        self._session_id = session_id
        self._data: Dict[str, Any] = {}

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, data: Dict[str, Any]) -> None:
        self._data.update(data)

    def delete(self, key: str) -> bool:
        return self._data.pop(key, None) is not None

    def has(self, key: str) -> bool:
        return key in self._data

    def clear(self) -> None:
        self._data.clear()

    @property
    def size(self) -> int:
        return len(self._data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self._session_id,
            "data": dict(self._data),
        }
