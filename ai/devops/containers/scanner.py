"""Image scanner."""
from __future__ import annotations

import time
from typing import Any


class ImageScanner:
    def __init__(self) -> None:
        self._scans: list[dict[str, Any]] = []
    def scan(self, image: str) -> dict[str, Any]:
        vulnerabilities = []
        if "old" in image.lower():
            vulnerabilities = [{"severity": "high", "package": "openssl", "version": "1.0.1"}]
        result = {"image": image, "vulnerabilities": vulnerabilities, "critical": sum(1 for v in vulnerabilities if v["severity"] == "high"), "scanned_at": time.time()}
        self._scans.append(result)
        return result
    def get_scans(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._scans[-limit:]
    def count(self) -> int:
        return len(self._scans)
