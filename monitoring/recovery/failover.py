from __future__ import annotations

import logging
import time
from typing import Any, Callable


class FailoverManager:
    """Manages failover between primary and standby resources."""

    def __init__(self) -> None:
        self._primary: str = ""
        self._standby: str = ""
        self._active: str = ""
        self._is_failed_over: bool = False
        self._health_check: Callable[[str], bool] | None = None
        self._on_failover: list[Callable[[str, str], None]] = []
        self._logger = logging.getLogger("superdev.recovery.failover")

    def configure(self, primary: str, standby: str, health_check: Callable[[str], bool] | None = None) -> None:
        self._primary = primary
        self._standby = standby
        self._active = primary
        self._health_check = health_check

    def check_and_failover(self) -> bool:
        if not self._health_check:
            return False

        try:
            primary_healthy = self._health_check(self._primary)
        except Exception:
            primary_healthy = False

        if not primary_healthy and not self._is_failed_over:
            return self.failover()
        elif primary_healthy and self._is_failed_over:
            return self.failback()

        return False

    def failover(self) -> bool:
        if self._is_failed_over:
            return False
        old = self._active
        self._active = self._standby
        self._is_failed_over = True
        self._logger.warning("Failover: %s -> %s", old, self._active)
        for cb in self._on_failover:
            try:
                cb(old, self._active)
            except Exception:
                pass
        return True

    def failback(self) -> bool:
        if not self._is_failed_over:
            return False
        old = self._active
        self._active = self._primary
        self._is_failed_over = False
        self._logger.info("Failback: %s -> %s", old, self._active)
        for cb in self._on_failover:
            try:
                cb(old, self._active)
            except Exception:
                pass
        return True

    def on_failover(self, callback: Callable[[str, str], None]) -> None:
        self._on_failover.append(callback)

    @property
    def active(self) -> str:
        return self._active

    @property
    def is_failed_over(self) -> bool:
        return self._is_failed_over
