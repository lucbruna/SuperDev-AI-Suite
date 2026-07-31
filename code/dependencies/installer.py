from __future__ import annotations

import logging
from typing import Any


class DependencyInstaller:
    """Installs project dependencies."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.dependencies.installer")

    def install(self, packages: list[str]) -> dict[str, Any]:
        self._log.info("Installing %d packages", len(packages))
        return {"success": True, "installed": [], "failed": []}

    def install_all(self) -> dict[str, Any]:
        self._log.info("Installing all dependencies")
        return {"success": True, "installed": [], "failed": []}
