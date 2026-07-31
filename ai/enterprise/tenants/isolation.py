"""Tenant isolation."""
from __future__ import annotations
from typing import Any, Dict

class TenantIsolation:
    def __init__(self) -> None:
        self._isolation: Dict[str, str] = {}
    def set_level(self, org_id: str, level: str) -> None:
        self._isolation[org_id] = level
    def get_level(self, org_id: str) -> str:
        return self._isolation.get(org_id, "shared")
    def is_isolated(self, org_id: str) -> bool:
        return self.get_level(org_id) in ("dedicated", "isolated")
    def can_access(self, requester_org: str, target_org: str) -> bool:
        if requester_org == target_org:
            return True
        return not self.is_isolated(target_org)
    def list_by_level(self, level: str) -> list:
        return [org for org, l in self._isolation.items() if l == level]
    def remove(self, org_id: str) -> bool:
        if org_id in self._isolation:
            del self._isolation[org_id]
            return True
        return False
