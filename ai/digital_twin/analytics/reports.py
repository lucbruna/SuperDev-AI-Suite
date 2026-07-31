"""Analytics reports."""

from __future__ import annotations

import time
from typing import Any


class ReportGenerator:
    def __init__(self) -> None:
        self._reports: list[dict[str, Any]] = []

    def generate(self, title: str, data: dict[str, Any], format: str = "json") -> dict[str, Any]:
        report = {"title": title, "data": data, "format": format, "generated_at": time.time()}
        self._reports.append(report)
        return report

    def summary(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"keys": list(data.keys()), "total": len(data)}

    def get_reports(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._reports[-limit:]

    def count(self) -> int:
        return len(self._reports)

    def clear(self) -> int:
        n = len(self._reports)
        self._reports.clear()
        return n
