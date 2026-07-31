"""Tenant manager."""

from __future__ import annotations

from typing import Any


class TenantManager:
    def __init__(self) -> None:
        self._configs: dict[str, dict[str, Any]] = {}

    def set_config(self, org_id: str, key: str, value: Any) -> None:
        self._configs.setdefault(org_id, {})[key] = value

    def get_config(self, org_id: str, key: str, default: Any = None) -> Any:
        return self._configs.get(org_id, {}).get(key, default)

    def get_all_config(self, org_id: str) -> dict[str, Any]:
        return dict(self._configs.get(org_id, {}))

    def delete_config(self, org_id: str, key: str) -> bool:
        if org_id in self._configs and key in self._configs[org_id]:
            del self._configs[org_id][key]
            return True
        return False

    def list_tenants(self) -> list[str]:
        return list(self._configs.keys())
