from __future__ import annotations

import logging
import time
from typing import Any


class OfflineCache:
    """Caches data locally so the mobile surface works without connectivity."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.mobile.offline")
        self._store: dict[str, tuple[float, Any]] = {}
        self._ttl = 86400.0
        self._online = True

    def set_online(self, online: bool) -> None:
        self._online = online

    def is_online(self) -> bool:
        return self._online

    def put(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        ts, value = entry
        if time.time() - ts > self._ttl:
            self._store.pop(key, None)
            return None
        return value

    def invalidate(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        self._store.clear()

    def status(self) -> dict[str, Any]:
        return {"online": self._online, "entries": len(self._store)}
