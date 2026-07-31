"""Per-endpoint rate limiting middleware."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class EndpointRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with per-endpoint configuration.

    Args:
        app: ASGI application.
        endpoint_limits: Dict mapping path patterns to max requests per window.
            Example: {"/api/v1/ai/*": 10, "/api/v1/auth/*": 20, "default": 100}
        window_seconds: Time window in seconds for the sliding window.
    """

    def __init__(
        self,
        app: Any,
        endpoint_limits: dict[str, int] | None = None,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.endpoint_limits = endpoint_limits or {"default": 100}
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _match_limit(self, path: str) -> int:
        """Find the rate limit for a given path. Most specific match wins."""
        best_match = None
        best_len = -1
        for pattern, limit in self.endpoint_limits.items():
            if pattern == "default":
                continue
            # Simple glob-style matching: /api/v1/ai/* matches /api/v1/ai/completions
            if pattern.endswith("/*"):
                prefix = pattern[:-2]
                if path.startswith(prefix) and len(prefix) > best_len:
                    best_match = limit
                    best_len = len(prefix)
            elif pattern == path:
                return limit
        if best_match is not None:
            return best_match
        return self.endpoint_limits.get("default", 100)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        limit = self._match_limit(path)
        key = f"{client_ip}:{path}"

        now = time.time()
        window_start = now - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        if len(self._requests[key]) >= limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "path": path,
                    "limit": limit,
                    "window_seconds": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        self._requests[key].append(now)
        return await call_next(request)

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = time.time()
        window_start = now - self.window_seconds
        total = 0
        empty_keys = []
        for key, timestamps in self._requests.items():
            before = len(timestamps)
            self._requests[key] = [t for t in timestamps if t > window_start]
            total += before - len(self._requests[key])
            if not self._requests[key]:
                empty_keys.append(key)
        for k in empty_keys:
            del self._requests[k]
        return total
