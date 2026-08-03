"""Filesystem permissions — mode inspection and change (Vol 12, Fase 26)."""
from __future__ import annotations

import os
import stat
import sys
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class PermissionsManager:
    """Reads and changes file permission bits."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def read_mode(self, path: str) -> dict[str, Any]:
        require_filesystem_action("permissions")
        try:
            info = os.stat(path)
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        return {
            "ok": True,
            "path": str(path),
            "mode": oct(stat.S_IMODE(info.st_mode)),
            "size": info.st_size,
            "modified": info.st_mtime,
        }

    def chmod(self, path: str, mode: int) -> dict[str, Any]:
        require_filesystem_action("permissions")
        started = monotonic()
        try:
            os.chmod(path, mode)
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.chmod", monotonic() - started)
        self._logger.log("filesystem", f"chmod: {path} -> {oct(mode)}")
        return {
            "ok": True,
            "path": str(path),
            "mode": oct(mode),
            "platform": sys.platform,
        }


__all__ = ["PermissionsManager"]
