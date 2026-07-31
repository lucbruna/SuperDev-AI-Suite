"""Tenant engine."""

from __future__ import annotations

import time
from typing import Any


class TenantEngine:
    def __init__(self) -> None:
        self._tenants: dict[str, dict[str, Any]] = {}
        self._started = False

    def start(self) -> None:
        self._started = True

    def stop(self) -> None:
        self._started = False

    def create(self, org_id: str, isolation: str = "shared", config: dict[str, Any] | None = None) -> dict[str, Any]:
        tenant = {
            "org_id": org_id,
            "isolation": isolation,
            "config": config or {},
            "status": "active",
            "created_at": time.time(),
        }
        self._tenants[org_id] = tenant
        return tenant

    def get(self, org_id: str) -> dict[str, Any] | None:
        return self._tenants.get(org_id)

    def update(self, org_id: str, **kwargs: Any) -> dict[str, Any] | None:
        t = self._tenants.get(org_id)
        if t:
            t.update(kwargs)
            return t
        return None

    def delete(self, org_id: str) -> bool:
        if org_id in self._tenants:
            del self._tenants[org_id]
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._tenants.values())

    def count(self) -> int:
        return len(self._tenants)

    def is_running(self) -> bool:
        return self._started
