"""Analytics reports."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ReportGenerator:
    def __init__(self) -> None:
        self._reports: List[Dict[str, Any]] = []
    def generate(self, title: str, data: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        report = {"title": title, "data": data, "format": format, "generated_at": time.time()}
        self._reports.append(report)
        return report
    def summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"keys": list(data.keys()), "total": len(data)}
    def get_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._reports[-limit:]
    def count(self) -> int:
        return len(self._reports)
    def clear(self) -> int:
        n = len(self._reports)
        self._reports.clear()
        return n
