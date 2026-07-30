from __future__ import annotations

import time
from typing import Any, Callable


class TaskRetry:
    """Handles retry logic for failed tasks."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0) -> None:
        self._max_retries = max_retries
        self._base_delay = base_delay

    def should_retry(self, attempt: int) -> bool:
        return attempt < self._max_retries

    def get_delay(self, attempt: int) -> float:
        return self._base_delay * (2 ** attempt)

    def execute(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    time.sleep(self.get_delay(attempt))
        raise last_error  # type: ignore[misc]
