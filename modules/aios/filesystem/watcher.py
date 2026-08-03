"""Filesystem watcher — polling change detection with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import os
from pathlib import Path
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class FileWatcher:
    """Tracks a directory tree and reports created/modified/deleted files.

    Polling-based (stdlib only): snapshots (mtime, size) per relative path.
    """

    def __init__(self) -> None:
        self._base: Path | None = None
        self._snapshot: dict[str, tuple[float, int]] = {}
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    @staticmethod
    def _scan(base: Path) -> dict[str, tuple[float, int]]:
        snapshot: dict[str, tuple[float, int]] = {}
        for dirpath, _dirnames, filenames in os.walk(base):
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                try:
                    info = os.stat(full)
                except OSError:
                    continue
                rel = os.path.relpath(full, base)
                snapshot[rel] = (info.st_mtime, info.st_size)
        return snapshot

    def watch(self, path: str) -> dict[str, Any]:
        require_filesystem_action("watch")
        base = Path(path)
        if not base.is_dir():
            return {"ok": False, "reason": "not a directory"}
        self._base = base
        self._snapshot = self._scan(base)
        self._logger.log("filesystem", f"watch: {path} -> {len(self._snapshot)} tracked")
        return {"ok": True, "path": str(path), "tracked": len(self._snapshot)}

    def changes(self, *, refresh: bool = True) -> dict[str, Any]:
        require_filesystem_action("watch")
        started = monotonic()
        if self._base is None:
            return {"created": [], "modified": [], "deleted": []}
        current = self._scan(self._base)
        created = sorted(set(current) - set(self._snapshot))
        deleted = sorted(set(self._snapshot) - set(current))
        modified = sorted(
            rel
            for rel in set(current) & set(self._snapshot)
            if current[rel] != self._snapshot[rel]
        )
        if refresh:
            self._snapshot = current
        self._metrics.record_timing("filesystem.watch", monotonic() - started)
        self._logger.log(
            "filesystem",
            f"watch changes: +{len(created)} ~{len(modified)} -{len(deleted)}",
        )
        return {"created": created, "modified": modified, "deleted": deleted}


__all__ = ["FileWatcher"]
