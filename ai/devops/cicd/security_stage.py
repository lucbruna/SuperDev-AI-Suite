"""Security stage."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class SecurityStage:
    def __init__(self) -> None:
        self._scans: List[Dict[str, Any]] = []
    def scan(self, project: str, scan_type: str = "sast") -> Dict[str, Any]:
        import uuid
        scan_id = str(uuid.uuid4())[:8]
        scan = {"scan_id": scan_id, "project": project, "type": scan_type, "vulnerabilities": 0, "status": "passed", "timestamp": time.time()}
        self._scans.append(scan)
        return scan
    def get_scan(self, scan_id: str) -> Dict[str, Any]:
        for s in self._scans:
            if s["scan_id"] == scan_id:
                return s
        return {"error": "not_found"}
    def list_scans(self, project: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        scans = self._scans
        if project:
            scans = [s for s in scans if s["project"] == project]
        return scans[-limit:]
    def count(self) -> int:
        return len(self._scans)
