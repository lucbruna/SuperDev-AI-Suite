import os
import time
from collections import defaultdict
from typing import Any

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with Redis-backed distributed storage.

    Falls back to in-memory storage when Redis is unavailable.
    """

    def __init__(
        self,
        app: Any,
        max_requests: int = 100,
        window_seconds: int = 60,
        redis_client: Any | None = None,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.redis_client = redis_client
        # Try to connect to Redis if not provided
        if self.redis_client is None:
            self._try_connect_redis()

    def _try_connect_redis(self) -> None:
        """Attempt to connect to Redis for distributed rate limiting."""
        try:
            import redis.asyncio as aioredis
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = aioredis.from_url(
                redis_url, decode_responses=True, socket_connect_timeout=2
            )
        except Exception:
            self.redis_client = None

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        client_ip = request.client.host if request.client else "unknown"

        if self.redis_client:
            is_limited = await self._check_redis(client_ip)
        else:
            is_limited = self._check_memory(client_ip)

        if is_limited:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(self.window_seconds)},
            )

        return await call_next(request)

    def _check_memory(self, client_ip: str) -> bool:
        """In-memory sliding window rate check."""
        now = time.time()
        window_start = now - self.window_seconds
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > window_start]
        if len(self.requests[client_ip]) >= self.max_requests:
            return True
        self.requests[client_ip].append(now)
        return False

    async def _check_redis(self, client_ip: str) -> bool:
        """Redis-based sliding window rate check using sorted sets."""

        now = time.time()
        window_start = now - self.window_seconds
        key = f"rate_limit:{client_ip}"

        pipe = self.redis_client.pipeline()
        # Remove expired entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Count current window
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiry
        pipe.expire(key, self.window_seconds)

        results = await pipe.execute()
        current_count = results[1]

        if current_count >= self.max_requests:
            # Remove the request we just added since we're rejecting it
            await self.redis_client.zrem(key, str(now))
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove expired entries from in-memory store. Returns count removed."""
        now = time.time()
        window_start = now - self.window_seconds
        total_removed = 0
        empty_keys = []

        for client_ip, timestamps in self.requests.items():
            before = len(timestamps)
            self.requests[client_ip] = [t for t in timestamps if t > window_start]
            total_removed += before - len(self.requests[client_ip])
            if not self.requests[client_ip]:
                empty_keys.append(client_ip)

        for key in empty_keys:
            del self.requests[key]

        return total_removed


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance.

    States:
    - closed: Normal operation, requests pass through
    - open: Too many failures, requests are rejected immediately
    - half-open: After recovery timeout, one test request is allowed through
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "closed"

    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

    async def call_async(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Async version of call for use with async functions."""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        try:
            result = await func(*args, **kwargs)
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = 0.0

    def is_available(self) -> bool:
        """Check if the circuit breaker would allow a request."""
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                return True
        return False
