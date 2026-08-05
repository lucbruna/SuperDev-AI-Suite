"""Periodic scheduler for intelligence tasks (mirrors architecture_graph)."""
from __future__ import annotations

import threading
import time
from typing import Any, Callable

MIN_INTERVAL = 0.05


class PeriodicRunner:
    """Runs a callback on an interval from a daemon thread."""

    def __init__(self, interval_seconds: float, task: Callable[[], Any], name: str = "intelligence") -> None:
        self.interval = max(interval_seconds, MIN_INTERVAL)
        self.task = task
        self.name = name
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name=f"ai-{self.name}", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _loop(self) -> None:
        next_due = time.monotonic()
        while not self._stop.is_set():
            next_due += self.interval
            try:
                self.task()
            except Exception:  # pragma: no cover - defensive
                pass
            delay = max(next_due - time.monotonic(), MIN_INTERVAL)
            self._sleep_delta(delay)

    def _sleep_delta(self, delay: float) -> None:
        self._stop.wait(timeout=delay)


_runner: PeriodicRunner | None = None


def get_runner() -> PeriodicRunner | None:
    return _runner


def start_background_runner(interval_seconds: float, task: Callable[[], Any]) -> PeriodicRunner:
    global _runner
    if _runner is not None:
        _runner.stop()
    _runner = PeriodicRunner(interval_seconds, task)
    _runner.start()
    return _runner


def stop_runner() -> None:
    global _runner
    if _runner is not None:
        _runner.stop()
        _runner = None
