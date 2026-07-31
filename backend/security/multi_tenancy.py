"""Multi-tenant management backed by PostgreSQL via Organization model.

The Organization table already stores: id, name, slug, plan, settings.
This module wraps it with tenant-aware limit checks and usage tracking.

TenantPlan maps to Organization.plan.
TenantManager delegates persistence to SQLAlchemy / Organization model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# ------------------------------------------------------------------
# Plan definitions (kept here as business-logic constants)
# ------------------------------------------------------------------


class TenantPlan:
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
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


PLAN_LIMITS: dict[str, TenantLimits] = {
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


def get_limits_for_plan(plan: str) -> TenantLimits:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS[TenantPlan.FREE])


# ------------------------------------------------------------------
# Tenant data object (read from DB, not stored separately)
# ------------------------------------------------------------------


@dataclass
class TenantView:
    """Read-only view of an Organization as a tenant."""

    id: str
    name: str
    slug: str
    plan: str = TenantPlan.FREE
    owner_id: str = ""
    is_active: bool = True
    settings: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def limits(self) -> TenantLimits:
        return get_limits_for_plan(self.plan)

    def check_limit(self, resource: str) -> bool:
        current = self.usage.get(resource, 0)
        limit_attr = f"max_{resource}"
        limit_val = getattr(self.limits, limit_attr, None)
        if limit_val is None:
            return True
        return current < limit_val

    def increment_usage(self, resource: str, amount: int = 1) -> None:
        self.usage[resource] = self.usage.get(resource, 0) + amount

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "plan": self.plan,
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


# ------------------------------------------------------------------
# Database-backed TenantManager
# ------------------------------------------------------------------


class TenantManager:
    """Multi-tenant management backed by PostgreSQL.

    Uses Organization + OrganizationMember tables for persistence.
    """

    async def create_tenant(
        self,
        db: AsyncSession,
        name: str,
        slug: str,
        owner_id: str,
        plan: str = TenantPlan.FREE,
        settings: dict[str, Any] | None = None,
    ) -> TenantView:
        from backend.database.models.organization import Organization, OrganizationMember

        # Check slug uniqueness
        existing = await db.execute(select(Organization).where(Organization.slug == slug))
        if existing.scalar_one_or_none():
            raise ValueError(f"Tenant slug already exists: {slug}")

        org = Organization(
            name=name,
            slug=slug,
            plan=plan,
            settings=settings or {},
        )
        db.add(org)
        await db.flush()

        # Add owner as a member
        member = OrganizationMember(
            organization_id=org.id,
            user_id=owner_id,
            role="owner",
        )
        db.add(member)
        await db.commit()
        await db.refresh(org)

        return TenantView(
            id=str(org.id),
            name=org.name,
            slug=org.slug,
            plan=org.plan,
            owner_id=owner_id,
            is_active=True,
            settings=org.settings or {},
        )

    async def get_tenant(self, db: AsyncSession, tenant_id: str) -> TenantView | None:
        from backend.database.models.organization import Organization

        org = await db.get(Organization, tenant_id)
        if not org:
            return None
        return self._org_to_view(org)

    async def get_tenant_by_slug(self, db: AsyncSession, slug: str) -> TenantView | None:
        from backend.database.models.organization import Organization

        result = await db.execute(select(Organization).where(Organization.slug == slug))
        org = result.scalar_one_or_none()
        if not org:
            return None
        return self._org_to_view(org)

    async def list_tenants(
        self,
        db: AsyncSession,
        owner_id: str | None = None,
    ) -> list[TenantView]:
        from backend.database.models.organization import Organization, OrganizationMember

        if owner_id:
            # Get org IDs where user is owner
            member_result = await db.execute(
                select(OrganizationMember.organization_id).where(OrganizationMember.user_id == owner_id)
            )
            org_ids = [row[0] for row in member_result.all()]
            if not org_ids:
                return []
            result = await db.execute(select(Organization).where(Organization.id.in_(org_ids)))
        else:
            result = await db.execute(select(Organization))

        return [self._org_to_view(org) for org in result.scalars().all()]

    async def upgrade_plan(
        self,
        db: AsyncSession,
        tenant_id: str,
        new_plan: str,
    ) -> TenantView | None:
        from backend.database.models.organization import Organization

        org = await db.get(Organization, tenant_id)
        if not org:
            return None
        org.plan = new_plan
        db.add(org)
        await db.commit()
        await db.refresh(org)
        return self._org_to_view(org)

    async def add_user(
        self,
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
    ) -> bool:
        from backend.database.models.organization import Organization, OrganizationMember

        org = await db.get(Organization, tenant_id)
        if not org or not org.is_active:
            return False

        # Check limit
        tenant_view = self._org_to_view(org)
        if not tenant_view.check_limit("users"):
            return False

        # Check if already a member
        existing = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == tenant_id,
                OrganizationMember.user_id == user_id,
            )
        )
        if existing.scalar_one_or_none():
            return True

        member = OrganizationMember(
            organization_id=tenant_id,
            user_id=user_id,
            role="member",
        )
        db.add(member)
        await db.commit()
        return True

    async def remove_user(
        self,
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
    ) -> bool:
        from backend.database.models.organization import OrganizationMember

        result = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == tenant_id,
                OrganizationMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            return False
        if member.role == "owner":
            return False  # Cannot remove the owner
        await db.delete(member)
        await db.commit()
        return True

    async def get_user_tenants(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> list[TenantView]:
        from backend.database.models.organization import Organization, OrganizationMember

        member_result = await db.execute(
            select(OrganizationMember.organization_id).where(OrganizationMember.user_id == user_id)
        )
        org_ids = [row[0] for row in member_result.all()]
        if not org_ids:
            return []

        result = await db.execute(select(Organization).where(Organization.id.in_(org_ids)))
        return [self._org_to_view(org) for org in result.scalars().all()]

    async def check_tenant_limit(
        self,
        db: AsyncSession,
        tenant_id: str,
        resource: str,
    ) -> bool:
        tenant = await self.get_tenant(db, tenant_id)
        if not tenant:
            return False
        return tenant.check_limit(resource)

    async def delete_tenant(
        self,
        db: AsyncSession,
        tenant_id: str,
    ) -> bool:
        from backend.database.models.organization import Organization

        org = await db.get(Organization, tenant_id)
        if not org:
            return False
        await db.delete(org)
        await db.commit()
        return True

    @staticmethod
    def _org_to_view(org: Any) -> TenantView:
        return TenantView(
            id=str(org.id),
            name=org.name,
            slug=org.slug,
            plan=org.plan,
            owner_id="",
            is_active=org.is_active if hasattr(org, "is_active") else True,
            settings=org.settings or {},
        )


# Global instance (no state — state lives in DB)
tenant_manager = TenantManager()
