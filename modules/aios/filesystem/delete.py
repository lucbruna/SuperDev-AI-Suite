"""Filesystem delete — safe deletion with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import shutil
from pathlib import Path
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class FileDeleter:
    """Deletes files and directories with safety guards."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    @staticmethod
    def _refused(path: Path) -> bool:
        try:
            resolved = path.resolve()
        except OSError:
            return False
        protected = {Path.cwd().resolve(), Path.home().resolve()}
        if resolved in protected:
            return True
        return resolved == resolved.anchor

    def delete_file(self, path: str) -> dict[str, Any]:
        require_filesystem_action("delete")
        started = monotonic()
        target = Path(path)
        if self._refused(target):
            return {"ok": False, "reason": "refused"}
        try:
            target.unlink()
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.delete", monotonic() - started)
        self._logger.log("filesystem", f"delete_file: {path}")
        return {"ok": True, "path": str(path), "removed": True}

    def delete_dir(self, path: str, *, recursive: bool = False) -> dict[str, Any]:
        require_filesystem_action("delete")
        started = monotonic()
        target = Path(path)
        if self._refused(target):
            return {"ok": False, "reason": "refused"}
        try:
            if any(target.iterdir()) and not recursive:
                return {"ok": False, "reason": "not empty"}
            shutil.rmtree(target)
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.delete_dir", monotonic() - started)
        self._logger.log("filesystem", f"delete_dir: {path}")
        return {"ok": True, "path": str(path), "removed": True}


__all__ = ["FileDeleter"]
