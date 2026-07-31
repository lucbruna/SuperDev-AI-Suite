from __future__ import annotations

import logging
from typing import Any


class FrontendRuntime:
    """Runtime environment for the frontend platform."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.runtime")
        self._services: dict[str, Any] = {}
        self._running: bool = False

    def start(self) -> bool:
        self._running = True
        self._log.info("frontend runtime started")
        return True

    def stop(self) -> bool:
        self._running = False
        self._log.info("frontend runtime stopped")
        return True

    def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service

    def get_service(self, name: str) -> Any:
        return self._services.get(name)

    def loop(self) -> None:
        if not self._running:
            raise RuntimeError("frontend runtime is not running")
