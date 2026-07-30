from __future__ import annotations

import logging
from typing import Any


class ProcessManager:
    """Manages child processes for code execution."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.execution.process")
        self._processes: dict[str, Any] = {}

    def start(self, cmd: list[str], env: dict[str, str] | None = None) -> str:
        pid = str(id(cmd))
        self._processes[pid] = {"cmd": cmd, "status": "running"}
        self._log.info("Started process %s: %s", pid, cmd)
        return pid

    def stop(self, pid: str) -> bool:
        if pid in self._processes:
            self._processes[pid]["status"] = "stopped"
            return True
        return False

    def list_processes(self) -> list[dict[str, Any]]:
        return list(self._processes.values())
