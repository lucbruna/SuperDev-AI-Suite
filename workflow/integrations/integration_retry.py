from __future__ import annotations

import logging
import time
from typing import Any, Callable


class IntegrationRetry:
    """Retry logic for integration calls."""

    def __init__(self, max_retries: int = 3, delay: float = 1.0) -> None:
        self._max_retries = max_retries
        self._delay = delay
        self._log = logging.getLogger("superdev.workflow.integrations.retry")

    def execute(self, action: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                return action(*args, **kwargs)
            except Exception as exc:
                last_error = exc
                self._log.warning("Attempt %d failed: %s", attempt, exc)
                if attempt < self._max_retries:
                    time.sleep(self._delay * attempt)
        raise last_error  # type: ignore[misc]
