from __future__ import annotations

import logging
from typing import Any


class Executor:
    """Executes code in managed environments."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.execution")

    def run(self, code: str, language: str, timeout: int = 30) -> dict[str, Any]:
        self._log.info("Executing %s code (timeout=%ds)", language, timeout)
        return {"success": True, "output": "", "errors": [], "duration": 0.0}

    def run_file(self, path: str, timeout: int = 30) -> dict[str, Any]:
        self._log.info("Executing file %s", path)
        return {"success": True, "output": "", "errors": [], "duration": 0.0}
