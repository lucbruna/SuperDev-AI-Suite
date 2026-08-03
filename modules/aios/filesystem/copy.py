"""Filesystem copy — file and directory copy with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import shutil
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class FileCopy:
    """Copies files and directories via shutil."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def copy_file(
        self,
        source: str,
        target: str,
        *,
        overwrite: bool = True,
    ) -> dict[str, Any]:
        require_filesystem_action("copy")
        started = monotonic()
        try:
            if not overwrite and __import__("os").path.exists(target):
                return {"ok": False, "reason": "exists"}
            shutil.copy2(source, target)
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        size = __import__("os").path.getsize(target)
        self._metrics.record_timing("filesystem.copy", monotonic() - started)
        self._logger.log("filesystem", f"copy: {source} -> {target}")
        return {"ok": True, "source": str(source), "target": str(target), "bytes": size}

    def copy_dir(
        self, source: str, target: str, *, ignore: list[str] | None = None
    ) -> dict[str, Any]:
        require_filesystem_action("copy")
        started = monotonic()
        try:
            shutil.copytree(source, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*(ignore or [])))
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        entries = sum(1 for _ in __import__("os").walk(target))
        self._metrics.record_timing("filesystem.copy_dir", monotonic() - started)
        self._logger.log("filesystem", f"copy_dir: {source} -> {target}")
        return {"ok": True, "source": str(source), "target": str(target), "entries": entries}


__all__ = ["FileCopy"]
