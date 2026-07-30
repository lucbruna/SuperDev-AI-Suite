from __future__ import annotations

import logging
import random
import time
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RetryHandler:
    """Configurable retry logic with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ) -> None:
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._exponential_base = exponential_base
        self._jitter = jitter
        self._logger = logging.getLogger("superdev.recovery.retry")

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        last_exception: Exception | None = None
        for attempt in range(1, self._max_retries + 2):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt > self._max_retries:
                    self._logger.error("All %d retries exhausted", self._max_retries)
                    raise

                delay = self._backoff(attempt)
                self._logger.warning(
                    "Attempt %d failed: %s. Retrying in %.1fs...",
                    attempt, e, delay,
                )
                time.sleep(delay)

        raise last_exception  # type: ignore[misc]

    def _backoff(self, attempt: int) -> float:
        delay = min(
            self._base_delay * (self._exponential_base ** (attempt - 1)),
            self._max_delay,
        )
        if self._jitter:
            delay *= 0.5 + random.random() * 0.5
        return delay

    def decorator(self, func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.execute(func, *args, **kwargs)
        return wrapper  # type: ignore[return-value]
