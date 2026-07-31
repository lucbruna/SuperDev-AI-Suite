"""Security stage."""

from __future__ import annotations

import time
from typing import Any


class SecurityStage:
    def __init__(self) -> None:
        self._scans: list[dict[str, Any]] = []

    def scan(self, project: str, scan_type: str = "sast") -> dict[str, Any]:
        import uuid

        scan_id = str(uuid.uuid4())[:8]
        scan = {
            "scan_id": scan_id,
            "project": project,
            "type": scan_type,
            "vulnerabilities": 0,
            "status": "passed",
            "timestamp": time.time(),
        }
        self._scans.append(scan)
        return scan

    def get_scan(self, scan_id: str) -> dict[str, Any]:
        for s in self._scans:
            if s["scan_id"] == scan_id:
                return s
        return {"error": "not_found"}

    def list_scans(self, project: str = "", limit: int = 20) -> list[dict[str, Any]]:
        scans = self._scans
        if project:
            scans = [s for s in scans if s["project"] == project]
        return scans[-limit:]

    def count(self) -> int:
        return len(self._scans)
