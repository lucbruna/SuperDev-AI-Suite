from __future__ import annotations

import logging
from typing import Any


class Builder:
    """Builds project artifacts from source."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.compilation.builder")

    def build(self, project_root: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        self._log.info("Building project at %s", project_root)
        return {"success": True, "artifacts": [], "duration": 0.0}

    def clean(self, project_root: str) -> None:
        self._log.info("Cleaning build artifacts at %s", project_root)
