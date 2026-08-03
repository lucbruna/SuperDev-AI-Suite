"""Filesystem package — local file operations with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

from modules.aios.filesystem.checksum import ChecksumManager
from modules.aios.filesystem.compression import CompressionManager
from modules.aios.filesystem.copy import FileCopy
from modules.aios.filesystem.delete import FileDeleter
from modules.aios.filesystem.filesystem import (
    FilesystemRuntime,
    get_filesystem_runtime,
    require_filesystem_action,
)
from modules.aios.filesystem.move import FileMover
from modules.aios.filesystem.permissions import PermissionsManager
from modules.aios.filesystem.search import FileSearch
from modules.aios.filesystem.watcher import FileWatcher

__all__ = [
    "ChecksumManager",
    "CompressionManager",
    "FileCopy",
    "FileDeleter",
    "FileMover",
    "FileSearch",
    "FileWatcher",
    "FilesystemRuntime",
    "PermissionsManager",
    "get_filesystem_runtime",
    "require_filesystem_action",
]
