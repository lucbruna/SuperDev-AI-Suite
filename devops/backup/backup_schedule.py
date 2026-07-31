from __future__ import annotations

import logging
from typing import Any


class BackupSchedule:
    """Schedules recurring backups."""

    def __init__(self, name: str, cron: str) -> None:
        self._log = logging.getLogger("superdev.devops.backup.schedule")
        self.name = name
        self.cron = cron
        self._jobs: list[dict[str, Any]] = []

    def start(self, engine: Any) -> dict[str, Any]:
        raise NotImplementedError

    def stop(self) -> bool:
        raise NotImplementedError

    def pause(self) -> bool:
        raise NotImplementedError

    def resume(self) -> bool:
        raise NotImplementedError

    def next_runs(self, count: int = 5) -> list[str]:
        raise NotImplementedError
