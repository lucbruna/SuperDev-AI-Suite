from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from backend.utils.uuid_utils import generate_uuid


class TenantPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TenantLimits:
    max_users: int = 5
    max_projects: int = 3
    max_storage_mb: int = 100
    max_api_calls_per_month: int = 10000
    max_agents: int = 2
    max_workflows: int = 5
    max_plugins: int = 3
    max_team_members: int = 5
    sso_enabled: bool = False
    audit_logging: bool = False
    custom_roles: bool = False
    priority_support: bool = False


PLAN_LIMITS = {
    TenantPlan.FREE: TenantLimits(),
    TenantPlan.PRO: TenantLimits(
        max_users=25,
        max_projects=20,
        max_storage_mb=5000,
        max_api_calls_per_month=500000,
        max_agents=10,
        max_workflows=50,
        max_plugins=20,
        max_team_members=25,
        sso_enabled=True,
        audit_logging=True,
        custom_roles=False,
        priority_support=True,
    ),
    TenantPlan.ENTERPRISE: TenantLimits(
        max_users=999999,
        max_projects=999999,
        max_storage_mb=999999,
        max_api_calls_per_month=999999999,
        max_agents=999999,
        max_workflows=999999,
        max_plugins=999999,
        max_team_members=999999,
        sso_enabled=True,
        audit_logging=True,
        custom_roles=True,
        priority_support=True,
    ),
}


@dataclass
class Tenant:
    id: str
    name: str
    slug: str
    plan: TenantPlan = TenantPlan.FREE
    owner_id: str = ""
    is_active: bool = True
    settings: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def limits(self) -> TenantLimits:
        return PLAN_LIMITS[self.plan]

    def check_limit(self, resource: str) -> bool:
        current = self.usage.get(resource, 0)
        limit_attr = f"max_{resource}"
        limit = getattr(self.limits, limit_attr, None)
        if limit is None:
            return True
        return current < limit

    def increment_usage(self, resource: str, amount: int = 1) -> None:
        self.usage[resource] = self.usage.get(resource, 0) + amount

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "plan": self.plan.value,
            "owner_id": self.owner_id,
            "is_active": self.is_active,
            "settings": self.settings,
            "usage": self.usage,
            "limits": {
                "max_users": self.limits.max_users,
                "max_projects": self.limits.max_projects,
                "max_storage_mb": self.limits.max_storage_mb,
                "sso_enabled": self.limits.sso_enabled,
                "audit_logging": self.limits.audit_logging,
                "custom_roles": self.limits.custom_roles,
            },
        }


class TenantManager:
    """Multi-tenant management system."""

    def __init__(self):
        self._tenants: dict[str, Tenant] = {}
        self._user_tenants: dict[str, list[str]] = {}

    def create_tenant(
        self,
        name: str,
        slug: str,
        owner_id: str,
        plan: TenantPlan = TenantPlan.FREE,
        settings: dict[str, Any] | None = None,
    ) -> Tenant:
        if any(t.slug == slug for t in self._tenants.values()):
            raise ValueError(f"Tenant slug already exists: {slug}")

        tenant = Tenant(
            id=generate_uuid(),
            name=name,
            slug=slug,
            plan=plan,
            owner_id=owner_id,
            settings=settings or {},
        )

        self._tenants[tenant.id] = tenant

        if owner_id not in self._user_tenants:
            self._user_tenants[owner_id] = []
        self._user_tenants[owner_id].append(tenant.id)

        return tenant

    def get_tenant(self, tenant_id: str) -> Tenant | None:
        return self._tenants.get(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Tenant | None:
        for tenant in self._tenants.values():
            if tenant.slug == slug:
                return tenant
        return None

    def list_tenants(self, owner_id: str | None = None) -> list[Tenant]:
        if owner_id:
            tenant_ids = self._user_tenants.get(owner_id, [])
            return [self._tenants[tid] for tid in tenant_ids if tid in self._tenants]
        return list(self._tenants.values())

    def update_tenant(self, tenant_id: str, **kwargs) -> Tenant | None:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None
        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        return tenant

    def upgrade_plan(self, tenant_id: str, new_plan: TenantPlan) -> Tenant | None:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None
        tenant.plan = new_plan
        return tenant

    def add_user(self, tenant_id: str, user_id: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        if not tenant.check_limit("users"):
            return False

        if user_id not in self._user_tenants:
            self._user_tenants[user_id] = []
        if tenant_id not in self._user_tenants[user_id]:
            self._user_tenants[user_id].append(tenant_id)
            tenant.increment_usage("users")

        return True

    def remove_user(self, tenant_id: str, user_id: str) -> bool:
        if user_id in self._user_tenants:
            if tenant_id in self._user_tenants[user_id]:
                self._user_tenants[user_id].remove(tenant_id)
                tenant = self._tenants.get(tenant_id)
                if tenant and tenant.usage.get("users", 0) > 0:
                    tenant.usage["users"] -= 1
                return True
        return False

    def get_user_tenants(self, user_id: str) -> list[Tenant]:
        tenant_ids = self._user_tenants.get(user_id, [])
        return [self._tenants[tid] for tid in tenant_ids if tid in self._tenants]

    def check_tenant_limit(self, tenant_id: str, resource: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        return tenant.check_limit(resource)

    def delete_tenant(self, tenant_id: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False

        for user_id in list(self._user_tenants.keys()):
            if tenant_id in self._user_tenants[user_id]:
                self._user_tenants[user_id].remove(tenant_id)

        del self._tenants[tenant_id]
        return True


tenant_manager = TenantManager()
