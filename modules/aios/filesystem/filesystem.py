"""Filesystem — facade over local file operations with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.filesystem.checksum import ChecksumManager
from modules.aios.filesystem.compression import CompressionManager
from modules.aios.filesystem.copy import FileCopy
from modules.aios.filesystem.delete import FileDeleter
from modules.aios.filesystem.move import FileMover
from modules.aios.filesystem.permissions import PermissionsManager
from modules.aios.filesystem.search import FileSearch
from modules.aios.filesystem.watcher import FileWatcher
from modules.aios.kernel.kernel_logger import get_kernel_logger


class FilesystemRuntime:
    """Facade over local filesystem operations.

    Stateless: every operation is stdlib-based and self-contained. ``close``
    is a no-op. The filesystem is always available.
    """

    def __init__(self) -> None:
        self.copy = FileCopy()
        self.move = FileMover()
        self.delete = FileDeleter()
        self.permissions = PermissionsManager()
        self.search = FileSearch()
        self.checksum = ChecksumManager()
        self.compression = CompressionManager()
        self.watcher = FileWatcher()
        self._logger = get_kernel_logger()

    async def available(self) -> bool:
        return True

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort inventory of the local filesystem."""
        try:
            usage = shutil.disk_usage(Path.cwd())
            return {
                "available": True,
                "platform": sys.platform,
                "cwd": str(Path.cwd()),
                "home": str(Path.home()),
                "temp": tempfile.gettempdir(),
                "disk_free_bytes": usage.free,
                "disk_total_bytes": usage.total,
            }
        except OSError:
            return {"available": True, "platform": sys.platform}

    async def close(self) -> None:
        """No-op — the filesystem runtime is stateless."""


_filesystem_runtime: FilesystemRuntime | None = None


def get_filesystem_runtime() -> FilesystemRuntime:
    global _filesystem_runtime
    if _filesystem_runtime is None:
        _filesystem_runtime = FilesystemRuntime()
    return _filesystem_runtime


__all__ = ["FilesystemRuntime", "get_filesystem_runtime", "require_filesystem_action"]
