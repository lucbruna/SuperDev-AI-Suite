from __future__ import annotations

import time
from typing import Any

from .rbac import RBACEngine


class TenantManager:
    """Multi-tenant authorization manager with tenant-scoped RBAC."""

    def __init__(self) -> None:
        self._tenants: dict[str, dict[str, Any]] = {}
        self._tenant_membership: dict[str, dict[str, str]] = {}

    def create_tenant(
        self,
        tenant_id: str,
        name: str,
        config: dict[str, Any] | None = None,
    ) -> bool:
        if tenant_id in self._tenants:
            return False
        self._tenants[tenant_id] = {
            "tenant_id": tenant_id,
            "name": name,
            "config": config or {},
            "created_at": time.time(),
            "rbac": RBACEngine(),
        }
        self._tenant_membership[tenant_id] = {}
        return True

    def get_tenant(self, tenant_id: str) -> dict[str, Any] | None:
        return self._tenants.get(tenant_id)

    def assign_user_to_tenant(self, user_id: str, tenant_id: str, role: str = "viewer") -> bool:
        tenant = self._tenants.get(tenant_id)
        if tenant is None:
            return False
        if tenant_id not in self._tenant_membership:
            self._tenant_membership[tenant_id] = {}
        self._tenant_membership[tenant_id][user_id] = role
        tenant["rbac"].assign_role_to_user(user_id, role)
        return True

    def remove_user_from_tenant(self, user_id: str, tenant_id: str) -> bool:
        membership = self._tenant_membership.get(tenant_id, {})
        if user_id in membership:
            del membership[user_id]
            tenant = self._tenants.get(tenant_id)
            if tenant:
                tenant["rbac"].remove_role_from_user(user_id, "admin")
                tenant["rbac"].remove_role_from_user(user_id, "manager")
                tenant["rbac"].remove_role_from_user(user_id, "editor")
                tenant["rbac"].remove_role_from_user(user_id, "viewer")
            return True
        return False

    def get_user_tenants(self, user_id: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for tenant_id, members in self._tenant_membership.items():
            if user_id in members:
                tenant = self._tenants.get(tenant_id)
                if tenant:
                    result.append({
                        "tenant_id": tenant_id,
                        "name": tenant["name"],
                        "role": members[user_id],
                    })
        return result

    def check_tenant_access(self, user_id: str, tenant_id: str) -> bool:
        members = self._tenant_membership.get(tenant_id, {})
        return user_id in members

    def check_tenant_permission(self, user_id: str, tenant_id: str, permission: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        if tenant is None:
            return False
        if not self.check_tenant_access(user_id, tenant_id):
            return False
        return tenant["rbac"].check_permission(user_id, permission)

    def get_tenant_rbac(self, tenant_id: str) -> RBACEngine | None:
        tenant = self._tenants.get(tenant_id)
        return tenant.get("rbac") if tenant else None

    def list_tenants(self) -> list[dict[str, Any]]:
        return [
            {
                "tenant_id": t["tenant_id"],
                "name": t["name"],
                "member_count": len(self._tenant_membership.get(t["tenant_id"], {})),
            }
            for t in self._tenants.values()
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenants": self.list_tenants(),
            "total_tenants": len(self._tenants),
        }
