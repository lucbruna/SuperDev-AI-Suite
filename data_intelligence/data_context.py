"""Execution context for the Data Intelligence Engine."""

from __future__ import annotations

import threading
from typing import Any


class DataIntelligenceContext:
    """Holds attributes for the current operation (thread-local)."""

    def __init__(self) -> None:
        self._local = threading.local()

    def _get_store(self) -> dict[str, Any]:
        store = getattr(self._local, "attributes", None)
        if store is None:
            store = {}
            self._local.attributes = store
        return store

    def set(self, key: str, value: Any) -> None:
        self._get_store()[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._get_store().get(key, default)

    def attributes(self) -> dict[str, Any]:
        return dict(self._get_store())

    def clear(self) -> None:
        self._local.attributes = {}
