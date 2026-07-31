from __future__ import annotations

import logging
from typing import Any


class RegistryCleanup:
    """Cleans up unused images and packages in registries."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.registry.cleanup")

    def dry_run(self, repository: str, policy: dict[str, Any]) -> list[str]:
        raise NotImplementedError

    def execute(self, repository: str, policy: dict[str, Any]) -> list[str]:
        raise NotImplementedError

    def untagged(self, repository: str) -> list[str]:
        raise NotImplementedError

    def older_than(self, repository: str, days: int) -> list[str]:
        raise NotImplementedError
