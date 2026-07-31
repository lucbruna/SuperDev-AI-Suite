"""Per-IP sliding-window rate limiter for authentication endpoints.

Prevents brute-force attacks on ``/login`` and ``/register``. In-memory by
design; for multi-worker deployments wire a shared store (Redis) instead.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class AuthRateLimiter:
    """In-memory sliding-window rate limiter keyed by client IP."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window = self._hits[client_ip]
        while window and now - window[0] > self._window_seconds:
            window.popleft()
        if len(window) >= self._max_requests:
            return False
        window.append(now)
        return True

    def reset(self, client_ip: str) -> None:
        self._hits.pop(client_ip, None)

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        if not self.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Try again later.",
                headers={"Retry-After": str(self._window_seconds)},
            )


login_limiter = AuthRateLimiter(max_requests=10, window_seconds=60)

__all__ = ["AuthRateLimiter", "login_limiter"]
