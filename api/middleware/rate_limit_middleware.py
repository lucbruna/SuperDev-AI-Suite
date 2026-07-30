from __future__ import annotations

import time
from typing import Any

from ..api_interfaces import IAPIMiddleware
from ..api_logger import APILogger
from ..api_models import APIResponse
from ..api_constants import RATE_LIMIT_HEADERS


class RateLimitMiddleware(IAPIMiddleware):
    """Rate limiting middleware using token bucket approach."""

    def __init__(
        self,
        default_max: int = 100,
        default_window: int = 60,
        logger: APILogger | None = None,
    ) -> None:
        self._default_max = default_max
        self._default_window = default_window
        self._buckets: dict[str, dict[str, Any]] = {}
        self._logger = logger or APILogger("api.ratelimit")

    def _get_bucket(self, key: str, max_requests: int, window_sec: int) -> dict[str, Any]:
        now = time.time()
        if key not in self._buckets:
            self._buckets[key] = {"tokens": max_requests, "last_refill": now, "max": max_requests, "window": window_sec}
        bucket = self._buckets[key]
        elapsed = now - bucket["last_refill"]
        refill = int(elapsed * (bucket["max"] / bucket["window"]))
        if refill > 0:
            bucket["tokens"] = min(bucket["max"], bucket["tokens"] + refill)
            bucket["last_refill"] = now
        return bucket

    async def before_request(self, request: Any) -> Any:
        client_ip = getattr(request, "client_ip", "") or "unknown"
        path = getattr(request, "path", "/")
        key = f"{client_ip}:{path}"

        max_req = self._default_max
        window = self._default_window
        if hasattr(request, "_rate_limit"):
            max_req = getattr(request, "_rate_limit", max_req)

        bucket = self._get_bucket(key, max_req, window)
        remaining = bucket["tokens"]

        if remaining <= 0:
            self._logger.warning("Rate limit exceeded", key=key)
            return APIResponse(
                status_code=429,
                body='{"error": "Too Many Requests", "code": "RATE_LIMIT_EXCEEDED"}',
                headers={
                    "content-type": "application/json",
                    RATE_LIMIT_HEADERS["limit"]: str(max_req),
                    RATE_LIMIT_HEADERS["remaining"]: "0",
                    RATE_LIMIT_HEADERS["reset"]: str(int(bucket["last_refill"] + bucket["window"])),
                    "retry-after": str(window),
                },
            )

        bucket["tokens"] -= 1
        if hasattr(request, "_rate_limit_headers"):
            request._rate_limit_headers = {
                RATE_LIMIT_HEADERS["limit"]: str(max_req),
                RATE_LIMIT_HEADERS["remaining"]: str(int(remaining - 1)),
                RATE_LIMIT_HEADERS["reset"]: str(int(bucket["last_refill"] + bucket["window"])),
            }
        return None

    async def after_request(self, response: Any) -> Any:
        if hasattr(response, "headers") and isinstance(response.headers, dict):
            if hasattr(response, "_context") and hasattr(response._context, "_rate_limit_headers"):
                response.headers.update(response._context._rate_limit_headers)
        return response

    def to_dict(self) -> dict[str, Any]:
        return {
            "middleware": "RateLimitMiddleware",
            "default_max": self._default_max,
            "default_window": self._default_window,
            "active_buckets": len(self._buckets),
        }
