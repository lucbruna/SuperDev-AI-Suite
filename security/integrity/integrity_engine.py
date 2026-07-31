"""Integrity subsystem (Volume 16) — checksums, tamper detection."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ..security_models import IntegrityReport


class IntegrityEngine:
    """Verify file/artifact integrity via checksums."""

    name = "integrity"
    description = "Checksum verification and tamper detection"

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._baselines: dict[str, str] = {}

    @staticmethod
    def checksum(data: bytes, algorithm: str = "sha256") -> str:
        if algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        if algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        return hashlib.sha256(data).hexdigest()

    def checksum_file(self, path: str | Path, algorithm: str = "sha256") -> str | None:
        try:
            return self.checksum(Path(path).read_bytes(), algorithm)
        except OSError:
            return None

    def set_baseline(self, target: str, checksum: str) -> None:
        self._baselines[target] = checksum

    def baseline(self, target: str) -> str | None:
        return self._baselines.get(target)

    def verify(self, target: str, data: bytes | None = None) -> IntegrityReport:
        """Verify a target against its stored baseline."""
        baseline = self._baselines.get(target)
        if baseline is None:
            return IntegrityReport(target=target, status="error", error="no baseline stored")
        if data is not None:
            current = self.checksum(data)
            report = IntegrityReport(
                target=target,
                status="ok" if current == baseline else "modified",
                checksum=current,
                expected_checksum=baseline,
                changed_files=[target] if current != baseline else [],
            )
        else:
            current = self.checksum_file(target)
            if current is None:
                report = IntegrityReport(target=target, status="missing", error="file not found")
            else:
                report = IntegrityReport(
                    target=target,
                    status="ok" if current == baseline else "modified",
                    checksum=current,
                    expected_checksum=baseline,
                    changed_files=[target] if current != baseline else [],
                )
        if self.engine is not None:
            self.engine.metrics.increment(
                "security.integrity_checks", labels={"status": report.status}
            )
        return report

    def register_and_verify(self, target: str, data: bytes) -> IntegrityReport:
        if target not in self._baselines:
            self.set_baseline(target, self.checksum(data))
            return IntegrityReport(
                target=target,
                status="ok",
                checksum=self._baselines[target],
                expected_checksum=self._baselines[target],
            )
        return self.verify(target, data)

    def status(self) -> dict[str, Any]:
        return {"baselines": len(self._baselines)}
