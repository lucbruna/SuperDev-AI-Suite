"""Limit engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class LimitEngine:
    def __init__(self) -> None:
        self._limits: Dict[str, Dict[str, float]] = {}
        self._usage: Dict[str, Dict[str, float]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def set_limit(self, org_id: str, resource: str, limit: float) -> None:
        self._limits.setdefault(org_id, {})[resource] = limit
    def get_limit(self, org_id: str, resource: str) -> float:
        return self._limits.get(org_id, {}).get(resource, float('inf'))
    def record_usage(self, org_id: str, resource: str, amount: float = 1.0) -> float:
        self._usage.setdefault(org_id, {})
        self._usage[org_id][resource] = self._usage[org_id].get(resource, 0) + amount
        return self._usage[org_id][resource]
    def get_usage(self, org_id: str, resource: str) -> float:
        return self._usage.get(org_id, {}).get(resource, 0.0)
    def is_over_limit(self, org_id: str, resource: str) -> bool:
        return self.get_usage(org_id, resource) > self.get_limit(org_id, resource)
    def remaining(self, org_id: str, resource: str) -> float:
        return max(0, self.get_limit(org_id, resource) - self.get_usage(org_id, resource))
    def usage_percent(self, org_id: str, resource: str) -> float:
        limit = self.get_limit(org_id, resource)
        if limit == 0 or limit == float('inf'):
            return 0.0
        return (self.get_usage(org_id, resource) / limit) * 100
    def list_limits(self, org_id: str) -> Dict[str, float]:
        return dict(self._limits.get(org_id, {}))
    def list_usage(self, org_id: str) -> Dict[str, float]:
        return dict(self._usage.get(org_id, {}))
    def reset_usage(self, org_id: str, resource: str = "") -> float:
        if resource:
            old = self._usage.get(org_id, {}).get(resource, 0)
            self._usage.get(org_id, {}).pop(resource, None)
            return old
        return sum(self._usage.pop(org_id, {}).values())
    def is_running(self) -> bool:
        return self._started
