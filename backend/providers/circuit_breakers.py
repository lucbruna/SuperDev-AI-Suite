"""Provider-specific circuit breakers for fault tolerance."""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger("superdev")

F = TypeVar("F", bound=Callable[..., Any])


class ProviderCircuitBreaker:
    """Circuit breaker per provider API.

    States:
    - closed: Normal operation, requests pass through
    - open: Too many failures, requests are rejected immediately
    - half-open: After recovery timeout, one test request is allowed through
    """

    def __init__(
        self,
        provider_name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> None:
        self.provider_name = provider_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._state = "closed"
        self._half_open_used = False

    @property
    def state(self) -> str:
        if self._state == "open" and time.time() - self._last_failure_time > self.recovery_timeout:
            self._state = "half-open"
            self._half_open_used = False
        return self._state

    def record_success(self) -> None:
        self._failure_count = 0
        if self._state in ("half-open", "open"):
            logger.info("Circuit breaker CLOSED for provider=%s", self.provider_name)
        self._state = "closed"

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning(
                "Circuit breaker OPENED for provider=%s (failures=%d)",
                self.provider_name,
                self._failure_count,
            )

    def is_available(self) -> bool:
        s = self.state
        return s in ("closed", "half-open")

    def allow_request(self) -> bool:
        s = self.state
        if s == "closed":
            return True
        if s == "half-open" and not self._half_open_used:
            self._half_open_used = True
            return True
        return False

    def reset(self) -> None:
        self._failure_count = 0
        self._state = "closed"
        self._last_failure_time = 0.0

    def get_status(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "state": self.state,
            "failure_count": self._failure_count,
            "last_failure": self._last_failure_time,
        }


# Global registry of provider circuit breakers
_provider_breakers: dict[str, ProviderCircuitBreaker] = {}


def get_provider_breaker(
    provider_name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
) -> ProviderCircuitBreaker:
    """Get or create a circuit breaker for a provider."""
    if provider_name not in _provider_breakers:
        _provider_breakers[provider_name] = ProviderCircuitBreaker(
            provider_name=provider_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
    return _provider_breakers[provider_name]


def circuit_breaked(
    provider_name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
) -> Callable[[F], F]:
    """Decorator that wraps a provider method with circuit breaker logic."""

    def decorator(func: F) -> F:
        breaker = get_provider_breaker(provider_name, failure_threshold, recovery_timeout)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not breaker.allow_request():
                raise ConnectionError(
                    f"Circuit breaker OPEN for provider={provider_name}. "
                    f"Service unavailable, retry after {breaker.recovery_timeout}s."
                )
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception:
                breaker.record_failure()
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not breaker.allow_request():
                raise ConnectionError(
                    f"Circuit breaker OPEN for provider={provider_name}. "
                    f"Service unavailable, retry after {breaker.recovery_timeout}s."
                )
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception:
                breaker.record_failure()
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def get_all_breaker_statuses() -> list[dict[str, Any]]:
    """Get status of all registered circuit breakers."""
    return [b.get_status() for b in _provider_breakers.values()]


def reset_all_breakers() -> None:
    """Reset all circuit breakers (useful for admin/health endpoints)."""
    for b in _provider_breakers.values():
        b.reset()
