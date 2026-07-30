from __future__ import annotations

import time
from typing import Any, Callable


class Retry:
    """Retry logic for GitHub API calls."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        last_exception: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    time.sleep(delay)
        raise last_exception  # type: ignore[misc]

    async def execute_async(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        import asyncio
        last_exception: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    await asyncio.sleep(delay)
        raise last_exception  # type: ignore[misc]

    @staticmethod
    def with_exponential_backoff(max_retries: int = 3) -> Retry:
        return Retry(max_retries=max_retries, base_delay=1.0, max_delay=60.0)

    @staticmethod
    def with_constant_backoff(delay: float = 5.0, max_retries: int = 3) -> Retry:
        return Retry(max_retries=max_retries, base_delay=delay, max_delay=delay)
