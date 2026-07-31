"""Usage engine."""
from __future__ import annotations

import time
from typing import Any


class UsageEngine:
    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def record(self, org_id: str, metric: str, quantity: float, unit: str = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        import uuid
        entry = {"id": str(uuid.uuid4())[:8], "org_id": org_id, "metric": metric, "quantity": quantity, "unit": unit, "metadata": metadata or {}, "timestamp": time.time()}
        self._records.append(entry)
        return entry
    def get_usage(self, org_id: str, metric: str = "", start: float = 0, end: float = 0) -> list[dict[str, Any]]:
        results = [r for r in self._records if r["org_id"] == org_id]
        if metric:
            results = [r for r in results if r["metric"] == metric]
        if start:
            results = [r for r in results if r["timestamp"] >= start]
        if end:
            results = [r for r in results if r["timestamp"] <= end]
        return results
    def total_usage(self, org_id: str, metric: str) -> float:
        return sum(r["quantity"] for r in self._records if r["org_id"] == org_id and r["metric"] == metric)
    def list_metrics(self, org_id: str) -> list[str]:
        return list(set(r["metric"] for r in self._records if r["org_id"] == org_id))
    def count(self) -> int:
        return len(self._records)
    def is_running(self) -> bool:
        return self._started
