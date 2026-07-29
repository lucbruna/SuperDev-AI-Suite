from __future__ import annotations as __

import hashlib
from typing import Dict


class TenantIsolation:
    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, str]] = {}

    def get_schema(self, tenant_id: str) -> str:
        sanitized = tenant_id.replace("-", "_").replace(".", "_")
        schema = f"tenant_{sanitized}"
        return schema

    def get_redis_prefix(self, tenant_id: str) -> str:
        return f"tenant:{tenant_id}"

    def get_storage_path(self, tenant_id: str) -> str:
        hash_part = hashlib.sha256(tenant_id.encode()).hexdigest()[:8]
        return f"tenants/{hash_part}/{tenant_id}"

    def isolate(self, tenant_id: str) -> Dict[str, str]:
        result = {
            "schema": self.get_schema(tenant_id),
            "redis_prefix": self.get_redis_prefix(tenant_id),
            "storage_path": self.get_storage_path(tenant_id),
        }
        self._cache[tenant_id] = result
        return result

    def get_isolation_config(self, tenant_id: str) -> Dict[str, str] | None:
        return self._cache.get(tenant_id)

    def build_connection_string(
        self, base_conn: str, tenant_id: str
    ) -> str:
        schema = self.get_schema(tenant_id)
        if "?" in base_conn:
            return f"{base_conn}&options=-csearch_path%3D{schema}"
        return f"{base_conn}?options=-csearch_path%3D{schema}"
