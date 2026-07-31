from __future__ import annotations

import logging
from typing import Any


class RegistryQuota:
    """Tracks and enforces registry storage quotas."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.registry.quota")
        self._usage: dict[str, dict[str, Any]] = {}

    def set_quota(self, repository: str, limit_bytes: int) -> None:
        raise NotImplementedError

    def usage(self, repository: str) -> dict[str, Any]:
        raise NotImplementedError

    def check(self, repository: str, additional_bytes: int) -> dict[str, Any]:
        raise NotImplementedError

    def report(self) -> dict[str, Any]:
        raise NotImplementedError
