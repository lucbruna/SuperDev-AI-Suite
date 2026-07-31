from __future__ import annotations

import time
from typing import Any


class Decay:
    """Applies decay to memory entries based on age and access patterns."""

    def __init__(self, base_decay_rate: float = 0.1):
        self._decay_rate = base_decay_rate
        self._access_log: dict[str, float] = {}

    @property
    def decay_rate(self) -> float:
        return self._decay_rate

    def record_access(self, key: str) -> None:
        self._access_log[key] = time.time()

    def last_access(self, key: str) -> float | None:
        return self._access_log.get(key)

    def decay_score(self, key: str, entry: dict[str, Any]) -> float:
        last_acc: float = self._access_log.get(key, entry.get("created_at", 0.0)) or 0.0
        age = time.time() - last_acc
        return 1.0 - min(1.0, age * self._decay_rate / 3600.0)

    def apply_decay(self, entries: dict[str, Any], threshold: float = 0.2) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for k, v in entries.items():
            score = self.decay_score(k, v)
            if score < threshold:
                result[k] = v
        return result

    def refresh(self, key: str) -> None:
        self.record_access(key)

    def clear(self) -> None:
        self._access_log.clear()
