"""Tenant storage."""
from __future__ import annotations
from typing import Any, Dict

class TenantStorage:
    def __init__(self, max_gb: int = 100) -> None:
        self._usage: Dict[str, float] = {}
        self._max = max_gb
    def record_usage(self, org_id: str, size_gb: float) -> float:
        self._usage[org_id] = self._usage.get(org_id, 0) + size_gb
        return self._usage[org_id]
    def get_usage(self, org_id: str) -> float:
        return self._usage.get(org_id, 0.0)
    def get_remaining(self, org_id: str) -> float:
        return max(0, self._max - self.get_usage(org_id))
    def is_over_limit(self, org_id: str) -> bool:
        return self.get_usage(org_id) > self._max
    def get_usage_percent(self, org_id: str) -> float:
        usage = self.get_usage(org_id)
        return (usage / self._max * 100) if self._max > 0 else 0
    def reset(self, org_id: str) -> float:
        old = self._usage.get(org_id, 0)
        self._usage[org_id] = 0
        return old
    def list_usage(self) -> Dict[str, float]:
        return dict(self._usage)
