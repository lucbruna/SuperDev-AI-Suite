from __future__ import annotations

import time
from typing import Any


class RetentionPolicy:
    """Manages data retention policies for monitoring storage."""

    def __init__(self, max_age_days: float = 30.0) -> None:
        self._max_age_days = max_age_days

    @property
    def max_age_days(self) -> float:
        return self._max_age_days

    @max_age_days.setter
    def max_age_days(self, value: float) -> None:
        self._max_age_days = max(1.0, value)

    def is_expired(self, timestamp: float) -> bool:
        age = time.time() - timestamp
        return age > self._max_age_days * 86400

    def apply(self, data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        cutoff = time.time() - self._max_age_days * 86400
        return {
            k: v for k, v in data.items()
            if v.get("timestamp", 0) >= cutoff
        }
