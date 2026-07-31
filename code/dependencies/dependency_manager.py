from __future__ import annotations

import logging
from typing import Any


class DependencyManager:
    """Manages project dependencies."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.dependencies")

    def add(self, name: str, version: str | None = None) -> None:
        self._log.info("Adding dependency %s==%s", name, version or "latest")

    def remove(self, name: str) -> None:
        self._log.info("Removing dependency %s", name)

    def list_dependencies(self) -> list[dict[str, Any]]:
        return []
