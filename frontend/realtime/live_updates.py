from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable

from .event_stream import EventStream


class LiveUpdates:
    """Periodic live-update ticker for dashboard widgets."""

    def __init__(self, events: EventStream) -> None:
        self._log = logging.getLogger("superdev.frontend.realtime.live")
        self._events = events
        self._channel = "live"
        self._running = False
        self._thread: threading.Thread | None = None
        self._interval = 1.0

    def start(self, interval: float = 1.0) -> bool:
        if self._running:
            return True
        self._interval = interval
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> bool:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        return True

    def is_running(self) -> bool:
        return self._running

    def subscribe(self, handler: Callable[[str, Any], None]) -> None:
        self._events.subscribe(self._channel, handler)

    def emit(self, data: Any) -> None:
        self._events.publish(self._channel, data)

    def _run(self) -> None:
        while self._running:
            self.emit({"tick": time.time()})
            time.sleep(self._interval)
