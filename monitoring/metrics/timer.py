from __future__ import annotations

import time
from typing import Any

from .histogram import Histogram


class Timer:
    """Measures elapsed time as a context manager."""

    def __init__(self, name: str, labels: dict[str, str] | None = None) -> None:
        self._hist = Histogram(name=name, labels=labels)
        self._start: float = 0.0

    def start(self) -> None:
        self._start = time.perf_counter()

    def stop(self) -> float:
        elapsed = (time.perf_counter() - self._start) * 1000
        self._hist.observe(elapsed)
        return elapsed

    def __enter__(self) -> Timer:
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop()

    @property
    def histogram(self) -> Histogram:
        return self._hist


__all__ = ["Timer"]
