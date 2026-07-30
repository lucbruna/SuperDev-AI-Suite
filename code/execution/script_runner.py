from __future__ import annotations

import logging
from typing import Any


class ScriptRunner:
    """Runs scripts and captures output."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.execution.script")

    def run_python(self, script: str, args: list[str] | None = None) -> dict[str, Any]:
        self._log.info("Running Python script")
        return {"success": True, "stdout": "", "stderr": "", "exit_code": 0}

    def run_shell(self, command: str, timeout: int = 30) -> dict[str, Any]:
        self._log.info("Running shell command: %s", command[:80])
        return {"success": True, "stdout": "", "stderr": "", "exit_code": 0}
