"""Retention analytics."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class RetentionAnalytics:
    def __init__(self) -> None:
        self._churns: List[Dict[str, Any]] = []
        self._retentions: Dict[str, Dict[str, Any]] = {}
    def record_churn(self, org_id: str, reason: str = "") -> Dict[str, Any]:
        entry = {"org_id": org_id, "reason": reason, "churned_at": time.time()}
        self._churns.append(entry)
        return entry
    def record_active(self, org_id: str, months_active: int = 1) -> None:
        self._retentions[org_id] = {"months_active": months_active, "last_active": time.time()}
    def churn_rate(self, total_customers: int) -> float:
        if total_customers == 0:
            return 0.0
        return (len(self._churns) / total_customers) * 100
    def retention_rate(self, total_customers: int) -> float:
        if total_customers == 0:
            return 100.0
        return ((total_customers - len(self._churns)) / total_customers) * 100
    def avg_lifetime(self) -> float:
        if not self._retentions:
            return 0.0
        return sum(r["months_active"] for r in self._retentions.values()) / len(self._retentions)
    def list_churns(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._churns[-limit:]
    def list_active(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._retentions)
    def churn_count(self) -> int:
        return len(self._churns)
    def active_count(self) -> int:
        return len(self._retentions)
