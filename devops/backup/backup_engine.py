from __future__ import annotations

import logging
from typing import Any

from ..devops_context import DevOpsContext


class BackupEngine:
    """Creates, restores, and schedules backups."""

    def __init__(self, context: DevOpsContext | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.backup")
        self._context = context
        self._jobs: dict[str, dict[str, Any]] = {}

    def create(self, name: str, target: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def restore(self, backup_id: str, target: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, backup_id: str) -> bool:
        raise NotImplementedError

    def list(self, target: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def schedule(self, name: str, cron: str, target: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def verify(self, backup_id: str) -> dict[str, Any]:
        raise NotImplementedError
