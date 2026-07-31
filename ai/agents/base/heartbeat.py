from __future__ import annotations

import time
from typing import Any


class Heartbeat:
    """Heartbeat signal for agent liveness."""

    def __init__(self, agent_id: str, interval: float = 10.0) -> None:
        self._agent_id = agent_id
        self._interval = interval
        self._last_beat: float | None = None
        self._beat_count: int = 0

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def interval(self) -> float:
        return self._interval

    @property
    def last_beat(self) -> float | None:
        return self._last_beat

    @property
    def beat_count(self) -> int:
        return self._beat_count

    def beat(self) -> None:
        self._last_beat = time.time()
        self._beat_count += 1

    def is_alive(self, timeout: float | None = None) -> bool:
        if self._last_beat is None:
            return False
        t = timeout or self._interval * 3
        return (time.time() - self._last_beat) < t

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "alive": self.is_alive(),
            "beat_count": self._beat_count,
            "last_beat": self._last_beat,
        }
