"""Filesystem compression — zip/tar with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import os
import tarfile
import zipfile
from pathlib import Path
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class CompressionManager:
    """Creates and extracts zip/tar archives with member-safe extraction."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def zip(self, source: str, target: str) -> dict[str, Any]:
        require_filesystem_action("compress")
        started = monotonic()
        src = Path(source)
        try:
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
                if src.is_dir():
                    entries = 0
                    for path in sorted(src.rglob("*")):
                        if path.is_file():
                            archive.write(path, path.relative_to(src))
                            entries += 1
                else:
                    archive.write(src, src.name)
                    entries = 1
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.zip", monotonic() - started)
        self._logger.log("filesystem", f"zip: {source} -> {target}")
        return {
            "ok": True,
            "source": str(source),
            "target": str(target),
            "entries": entries,
            "bytes": os.path.getsize(target),
        }

    def unzip(self, source: str, target: str) -> dict[str, Any]:
        require_filesystem_action("compress")
        started = monotonic()
        dest = Path(target)
        try:
            with zipfile.ZipFile(source) as archive:
                for member in archive.infolist():
                    resolved = (dest / member.filename).resolve()
                    if not resolved.is_relative_to(dest.resolve()):
                        return {"ok": False, "reason": "unsafe member"}
                archive.extractall(dest)
                entries = len(archive.infolist())
        except (OSError, zipfile.BadZipFile) as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.unzip", monotonic() - started)
        self._logger.log("filesystem", f"unzip: {source} -> {target}")
        return {"ok": True, "source": str(source), "target": str(target), "entries": entries}

    def tar(self, source: str, target: str, *, mode: str = "w:gz") -> dict[str, Any]:
        require_filesystem_action("compress")
        started = monotonic()
        src = Path(source)
        try:
            with tarfile.open(target, mode) as archive:
                if src.is_dir():
                    archive.add(src, arcname=src.name, recursive=True)
                    entries = sum(1 for _ in src.rglob("*")) + 1
                else:
                    archive.add(src, arcname=src.name)
                    entries = 1
        except (OSError, tarfile.TarError) as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.tar", monotonic() - started)
        self._logger.log("filesystem", f"tar: {source} -> {target}")
        return {
            "ok": True,
            "source": str(source),
            "target": str(target),
            "entries": entries,
            "bytes": os.path.getsize(target),
        }

    def untar(self, source: str, target: str) -> dict[str, Any]:
        require_filesystem_action("compress")
        started = monotonic()
        dest = Path(target)
        try:
            with tarfile.open(source) as archive:
                for member in archive.getmembers():
                    resolved = (dest / member.name).resolve()
                    if not resolved.is_relative_to(dest.resolve()):
                        return {"ok": False, "reason": "unsafe member"}
                archive.extractall(dest)
                entries = len(archive.getmembers())
        except (OSError, tarfile.TarError) as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.untar", monotonic() - started)
        self._logger.log("filesystem", f"untar: {source} -> {target}")
        return {"ok": True, "source": str(source), "target": str(target), "entries": entries}


__all__ = ["CompressionManager"]
