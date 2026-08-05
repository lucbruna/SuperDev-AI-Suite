"""Dependency-free periodic runner for graph maintenance jobs.

Runs scheduled callables on a daemon thread; each job is executed in a
worker thread so a slow build never blocks other jobs. Start/stop are
idempotent and safe to call from FastAPI lifespan hooks.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)

Job = Callable[[], Any]


class PeriodicRunner:
    """A tiny cron-like scheduler with a daemon loop thread."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: dict[str, tuple[Job, float]] = {}  # name -> (job, interval)
        self._next: dict[str, float] = {}
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def schedule(self, name: str, job: Job, *, interval_seconds: float) -> None:
        """Register or replace a recurring job."""
        # Floor guards against zero/negative intervals without blocking tests.
        interval = max(interval_seconds, 0.05)
        with self._lock:
            self._jobs[name] = (job, interval)
            self._next[name] = time.monotonic() + interval

    def unschedule(self, name: str) -> None:
        with self._lock:
            self._jobs.pop(name, None)
            self._next.pop(name, None)

    def jobs(self) -> dict[str, float]:
        with self._lock:
            return {name: interval for name, (_, interval) in self._jobs.items()}

    # --------------------------------------------------------------- lifecycle
    def start(self) -> None:
        with self._lock:
            if self.running:
                return
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._loop, name="architecture-graph-scheduler", daemon=True
            )
            self._thread.start()
            logger.info("Periodic runner started")

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not self._loop_thread():
            thread.join(timeout=3.0)
        with self._lock:
            self._thread = None

    @staticmethod
    def _loop_thread() -> threading.Thread | None:
        return threading.current_thread()

    # ------------------------------------------------------------------ loop
    def _loop(self) -> None:
        while not self._stop.is_set():
            self._tick()
            self._stop.wait(self._sleep_delta())

    def _sleep_delta(self) -> float:
        """Seconds until the next due job, clamped to [0.05, 1.0]."""
        now = time.monotonic()
        with self._lock:
            if not self._next:
                return 1.0
            next_run = min(self._next.values())
        return min(1.0, max(0.05, next_run - now))

    def _tick(self) -> None:
        now = time.monotonic()
        due: list[tuple[str, Job]] = []
        with self._lock:
            for name, (job, _) in self._jobs.items():
                next_run = self._next.get(name, now)
                if now >= next_run:
                    due.append((name, job))
                    self._next[name] = now + self._jobs[name][1]
        for name, job in due:
            threading.Thread(
                target=self._run_safe, args=(name, job), name=f"graph-job-{name}", daemon=True
            ).start()

    def _run_safe(self, name: str, job: Job) -> None:
        try:
            job()
        except Exception:
            logger.exception("Scheduled job '%s' failed", name)


_runner: PeriodicRunner | None = None
_runner_lock = threading.Lock()


def get_runner() -> PeriodicRunner:
    """Process-wide singleton runner."""
    global _runner
    if _runner is None:
        with _runner_lock:
            if _runner is None:
                _runner = PeriodicRunner()
    return _runner


def start_background_runner() -> PeriodicRunner:
    """Start the singleton runner and return it."""
    runner = get_runner()
    runner.start()
    return runner


def stop_runner() -> None:
    runner = get_runner()
    runner.stop()
