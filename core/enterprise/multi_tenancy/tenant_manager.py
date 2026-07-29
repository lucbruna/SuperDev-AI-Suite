from __future__ import annotations as __

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class TenantConfig(BaseModel):
    plan_tier: str = "free"
    region: str = "us-east-1"
    features: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)


class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: f"tenant_{uuid4().hex[:12]}")
    name: str
    domain: str
    config: TenantConfig = Field(default_factory=TenantConfig)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TenantManager:
    def __init__(self) -> None:
        self._tenants: Dict[str, Tenant] = {}
        self._domain_index: Dict[str, str] = {}

    async def create_tenant(
        self, name: str, domain: str, config: Optional[Dict[str, Any]] = None
    ) -> str:
        await asyncio.sleep(0.01)
        for tid, t in self._tenants.items():
            if t.domain == domain:
                raise ValueError(f"Tenant with domain {domain} already exists")

        tenant = Tenant(
            name=name,
            domain=domain,
            config=TenantConfig(**(config or {})),
        )
        self._tenants[tenant.id] = tenant
        self._domain_index[domain] = tenant.id
        return tenant.id

    async def get_tenant(self, tenant_id: str) -> Tenant | None:
        await asyncio.sleep(0.01)
        return self._tenants.get(tenant_id)

    async def get_tenant_by_domain(self, domain: str) -> Tenant | None:
        await asyncio.sleep(0.01)
        tid = self._domain_index.get(domain)
        if not tid:
            return None
        return self._tenants.get(tid)

    async def list_tenants(self) -> List[Tenant]:
        await asyncio.sleep(0.01)
        return list(self._tenants.values())

    async def update_tenant(
        self, tenant_id: str, config: Dict[str, Any]
    ) -> Tenant:
        await asyncio.sleep(0.01)
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        for key, value in config.items():
            if hasattr(tenant.config, key):
                setattr(tenant.config, key, value)
            elif key in ("name", "domain"):
                setattr(tenant, key, value)

        if "settings" in config:
            tenant.config.settings.update(config["settings"])

        tenant.updated_at = datetime.utcnow()
        return tenant

    async def delete_tenant(self, tenant_id: str) -> bool:
        await asyncio.sleep(0.01)
        tenant = self._tenants.pop(tenant_id, None)
        if not tenant:
            return False
        self._domain_index.pop(tenant.domain, None)
        return True

    async def isolate_data(self, tenant_id: str) -> Dict[str, str]:
        await asyncio.sleep(0.05)
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        return {
            "schema": f"tenant_{tenant_id.replace('-', '_')}",
            "redis_prefix": f"tenant:{tenant_id}",
            "storage_path": f"tenants/{tenant_id}",
            "status": "isolated",
        }
