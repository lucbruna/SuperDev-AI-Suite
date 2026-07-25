from __future__ import annotations

import random
from typing import Optional


class RetryPolicy:
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
    ):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        if attempt <= 0:
            return 0.0
        d = self.delay * (self.backoff_factor ** (attempt - 1))
        d = min(d, self.max_delay)
        jitter = random.uniform(0, d * 0.1)
        return d + jitter

    def should_retry(self, attempt: int, error: Optional[str] = None) -> bool:
        return attempt < self.max_retries
