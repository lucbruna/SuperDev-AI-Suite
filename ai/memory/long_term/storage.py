from __future__ import annotations

from typing import Any, Dict, List, Optional


class Storage:
    """In-memory storage backend for long-term memory data."""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    @property
    def count(self) -> int:
        return len(self._data)

    def put(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str) -> Any | None:
        return self._data.get(key)

    def delete(self, key: str) -> bool:
        return self._data.pop(key, None) is not None

    def has(self, key: str) -> bool:
        return key in self._data

    def keys(self) -> List[str]:
        return list(self._data.keys())

    def clear(self) -> None:
        self._data.clear()

    def get_all(self) -> Dict[str, Any]:
        return dict(self._data)

    def size_bytes(self) -> int:
        import json
        return len(json.dumps(self._data, default=str).encode("utf-8"))
