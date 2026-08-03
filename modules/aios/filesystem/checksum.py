"""Filesystem checksums — streaming hashing with kernel ACL (Vol 12, Fase 26)."""
from __future__ import annotations

import hashlib
from time import monotonic
from typing import Any

from modules.aios.filesystem.acl import require_filesystem_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics

_CHUNK = 64 * 1024


class ChecksumManager:
    """Computes and verifies file digests using stdlib hashlib."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def hash_file(
        self, path: str, *, algorithm: str = "sha256"
    ) -> dict[str, Any]:
        require_filesystem_action("checksum")
        started = monotonic()
        if algorithm not in hashlib.algorithms_available:
            return {"ok": False, "reason": "algorithm"}
        digest = hashlib.new(algorithm)
        total = 0
        try:
            with open(path, "rb") as handle:
                while True:
                    block = handle.read(_CHUNK)
                    if not block:
                        break
                    digest.update(block)
                    total += len(block)
        except OSError as exc:
            return {"ok": False, "reason": str(exc)}
        self._metrics.record_timing("filesystem.checksum", monotonic() - started)
        self._logger.log("filesystem", f"checksum: {path} ({algorithm})")
        return {
            "ok": True,
            "path": str(path),
            "algorithm": algorithm,
            "hexdigest": digest.hexdigest(),
            "bytes": total,
        }

    def hash_bytes(self, data: bytes, *, algorithm: str = "sha256") -> str:
        require_filesystem_action("checksum")
        return hashlib.new(algorithm, data).hexdigest()

    def verify(
        self, path: str, expected: str, *, algorithm: str = "sha256"
    ) -> dict[str, Any]:
        require_filesystem_action("checksum")
        result = self.hash_file(path, algorithm=algorithm)
        if not result.get("ok"):
            return result
        actual = result["hexdigest"]
        return {
            "ok": True,
            "valid": actual.lower() == expected.lower(),
            "expected": expected,
            "actual": actual,
        }


__all__ = ["ChecksumManager"]
