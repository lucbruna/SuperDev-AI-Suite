"""Runtime lifecycle for the automation engine."""

from __future__ import annotations

import logging

from .automation_events import AutomationEvents
from .automation_registry import AutomationRegistry


class AutomationRuntime:
    """Starts and stops the automation engine (idempotent)."""

    def __init__(self, registry: AutomationRegistry,
                 events: AutomationEvents) -> None:
        self._log = logging.getLogger("superdev.automation.runtime")
        self.registry = registry
        self.events = events
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            self._log.info("automation runtime already running")
            return
        self._running = True
        self._log.info("automation runtime started (workspace=%s)",
                       self.registry.snapshot()["workflows"])

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        self._log.info("automation runtime stopped")

    def status(self) -> dict[str, object]:
        return {
            "running": self._running,
            "registry": self.registry.snapshot(),
        }
