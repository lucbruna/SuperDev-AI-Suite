"""Filesystem search — recursive file discovery with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import os
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class FileSearch:
    """Finds files under a root by name, extension and size filters."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def find(
        self,
        root: str,
        *,
        name: str | None = None,
        ext: str | None = None,
        min_size: int | None = None,
        max_size: int | None = None,
        recursive: bool = True,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        require_filesystem_action("search")
        started = monotonic()
        if not os.path.isdir(root):
            return []
        needle = name.lower() if name else None
        suffix = ext.lower() if ext else None
        if suffix and not suffix.startswith("."):
            suffix = f".{suffix}"
        results: list[dict[str, Any]] = []
        for dirpath, dirnames, filenames in os.walk(root):
            if not recursive:
                dirnames[:] = []
            for filename in filenames:
                if needle and needle not in filename.lower():
                    continue
                if suffix and not filename.lower().endswith(suffix):
                    continue
                full = os.path.join(dirpath, filename)
                try:
                    info = os.stat(full)
                except OSError:
                    continue
                if min_size is not None and info.st_size < min_size:
                    continue
                if max_size is not None and info.st_size > max_size:
                    continue
                results.append(
                    {"path": full, "size": info.st_size, "mtime": info.st_mtime}
                )
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break
        self._metrics.record_timing("filesystem.search", monotonic() - started)
        self._logger.log("filesystem", f"search: {root} -> {len(results)} hits")
        return results


__all__ = ["FileSearch"]
