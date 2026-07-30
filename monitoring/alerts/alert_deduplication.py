from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from ..monitoring_models import Alert


class AlertDeduplication:
    """Prevents duplicate alerts from firing within a time window."""

    def __init__(self, window_seconds: float = 60.0) -> None:
        self._window = window_seconds
        self._recent: dict[str, float] = {}

    def is_duplicate(self, alert: Alert) -> bool:
        key = self._fingerprint(alert)
        now = time.time()

        if key in self._recent:
            last_seen = self._recent[key]
            if (now - last_seen) < self._window:
                return True

        self._recent[key] = now
        self._prune(now)
        return False

    def _fingerprint(self, alert: Alert) -> str:
        content = json.dumps(
            {
                "name": alert.name,
                "severity": alert.severity.value,
                "labels": alert.labels,
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.md5(content.encode()).hexdigest()

    def _prune(self, now: float) -> None:
        expired = [
            k for k, v in self._recent.items()
            if (now - v) > self._window
        ]
        for k in expired:
            del self._recent[k]

    def clear(self) -> None:
        self._recent.clear()
