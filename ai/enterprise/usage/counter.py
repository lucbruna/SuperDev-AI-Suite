"""Usage counter."""
from __future__ import annotations
from typing import Any, Dict

class UsageCounter:
    def __init__(self) -> None:
        self._counters: Dict[str, Dict[str, float]] = {}
    def increment(self, org_id: str, counter_name: str, amount: float = 1.0) -> float:
        self._counters.setdefault(org_id, {})
        self._counters[org_id][counter_name] = self._counters[org_id].get(counter_name, 0) + amount
        return self._counters[org_id][counter_name]
    def decrement(self, org_id: str, counter_name: str, amount: float = 1.0) -> float:
        self._counters.setdefault(org_id, {})
        self._counters[org_id][counter_name] = self._counters[org_id].get(counter_name, 0) - amount
        return self._counters[org_id][counter_name]
    def get(self, org_id: str, counter_name: str) -> float:
        return self._counters.get(org_id, {}).get(counter_name, 0.0)
    def set(self, org_id: str, counter_name: str, value: float) -> None:
        self._counters.setdefault(org_id, {})[counter_name] = value
    def get_all(self, org_id: str) -> Dict[str, float]:
        return dict(self._counters.get(org_id, {}))
    def reset(self, org_id: str, counter_name: str) -> float:
        old = self._counters.get(org_id, {}).get(counter_name, 0)
        self._counters.get(org_id, {}).pop(counter_name, None)
        return old
    def list_counters(self, org_id: str) -> list:
        return list(self._counters.get(org_id, {}).keys())
