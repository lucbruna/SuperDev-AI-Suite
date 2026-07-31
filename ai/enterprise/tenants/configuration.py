"""Tenant configuration."""
from __future__ import annotations

from typing import Any


class TenantConfiguration:
    DEFAULTS = {"max_users": 10, "max_agents": 2, "max_projects": 10, "storage_gb": 5, "support_level": "basic"}
    def __init__(self) -> None:
        self._configs: dict[str, dict[str, Any]] = {}
    def get(self, org_id: str) -> dict[str, Any]:
        return {**self.DEFAULTS, **self._configs.get(org_id, {})}
    def set(self, org_id: str, key: str, value: Any) -> None:
        self._configs.setdefault(org_id, {})[key] = value
    def set_many(self, org_id: str, values: dict[str, Any]) -> None:
        self._configs.setdefault(org_id, {}).update(values)
    def delete(self, org_id: str, key: str) -> bool:
        if org_id in self._configs and key in self._configs[org_id]:
            del self._configs[org_id][key]
            return True
        return False
    def reset(self, org_id: str) -> int:
        n = len(self._configs.get(org_id, {}))
        self._configs.pop(org_id, None)
        return n
