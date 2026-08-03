"""Filesystem move — file/directory move with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import shutil
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class FileMover:
    """Moves files and directories with shutil."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def move(self, source: str, target: str) -> dict[str, Any]:
        require_filesystem_action("move")
        started = monotonic()
        try:
            shutil.move(source, target)
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.move", monotonic() - started)
        self._logger.log("filesystem", f"move: {source} -> {target}")
        return {"ok": True, "source": str(source), "target": str(target)}


__all__ = ["FileMover"]
