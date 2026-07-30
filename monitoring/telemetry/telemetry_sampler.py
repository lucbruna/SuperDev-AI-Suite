from __future__ import annotations

import random
from typing import Any


class TelemetrySampler:
    """Controls sampling rate for telemetry events."""

    def __init__(self, rate: float = 1.0) -> None:
        self._rate = rate

    @property
    def rate(self) -> float:
        return self._rate

    @rate.setter
    def rate(self, value: float) -> None:
        self._rate = max(0.0, min(1.0, value))

    def should_sample(self, event: Any) -> bool:
        return random.random() < self._rate
