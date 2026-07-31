"""Experience replay buffer for reinforcement learning."""

from __future__ import annotations

import time
from typing import Any


class ExperienceReplay:
    """Stores and samples past experiences for learning."""

    def __init__(self, max_size: int = 1000) -> None:
        self._buffer: list[dict[str, Any]] = []
        self._max_size = max_size

    def store(self, experience: dict[str, Any]) -> None:
        entry = {**experience, "stored_at": time.time()}
        if len(self._buffer) >= self._max_size:
            self._buffer.pop(0)
        self._buffer.append(entry)

    def sample(self, count: int = 10) -> list[dict[str, Any]]:
        import random

        if len(self._buffer) <= count:
            return list(self._buffer)
        return random.sample(self._buffer, count)

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._buffer)

    def count(self) -> int:
        return len(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()
