"""Digital Twin context."""

from __future__ import annotations

import time
import uuid
from typing import Any


class TwinContext:
    def __init__(self) -> None:
        self._context: dict[str, Any] = {}
        self._session_id = str(uuid.uuid4())[:8]
        self._started_at = time.time()

    def set(self, key: str, value: Any) -> None:
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    def delete(self, key: str) -> bool:
        if key in self._context:
            del self._context[key]
            return True
        return False

    def get_all(self) -> dict[str, Any]:
        return {**self._context, "session_id": self._session_id, "started_at": self._started_at}

    def clear(self) -> None:
        self._context.clear()

    def session_id(self) -> str:
        return self._session_id

    def uptime(self) -> float:
        return time.time() - self._started_at
