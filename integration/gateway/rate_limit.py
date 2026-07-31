from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any


class RateLimiter:
    """Sliding-window rate limiting per client."""

    def __init__(self, limit: int = 100, window: float = 60.0) -> None:
        self._log = logging.getLogger("superdev.integration.gateway.rate_limit")
        self.limit = limit
        self.window = window
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, client_id: str) -> bool:
        now = time.monotonic()
        hits = self._hits[client_id]
        while hits and now - hits[0] > self.window:
            hits.pop(0)
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        return True

    def remaining(self, client_id: str) -> int:
        now = time.monotonic()
        hits = self._hits[client_id]
        while hits and now - hits[0] > self.window:
            hits.pop(0)
        return max(0, self.limit - len(hits))

    def reset(self, client_id: str) -> None:
        self._hits.pop(client_id, None)

    def snapshot(self) -> dict[str, Any]:
        return {
            "limit": self.limit,
            "window": self.window,
            "active_clients": len(self._hits),
        }
