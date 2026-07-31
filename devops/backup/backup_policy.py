from __future__ import annotations

import logging
from typing import Any


class BackupPolicy:
    """Defines backup retention and frequency policies."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger("superdev.devops.backup.policy")
        self.name = name
        self._spec: dict[str, Any] = {}

    def set_retention(self, daily: int = 7, weekly: int = 4, monthly: int = 12) -> "BackupPolicy":
        raise NotImplementedError

    def set_schedule(self, cron: str) -> "BackupPolicy":
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError
