from __future__ import annotations

import uuid


class Tenant:
    """A multi-tenant boundary isolating users and resources."""

    def __init__(self, tenant_id: str, name: str) -> None:
        self.tenant_id = tenant_id
        self.name = name

    def to_dict(self) -> dict:
        return {"tenant_id": self.tenant_id, "name": self.name}


class TenantManager:
    """Creates and manages tenants with strict user isolation."""

    def __init__(self) -> None:
        self._tenants: dict[str, Tenant] = {}
        self._users: dict[str, list[str]] = {}

    def create_tenant(self, name: str) -> Tenant:
        tenant_id = str(uuid.uuid4())
        tenant = Tenant(tenant_id, name)
        self._tenants[tenant_id] = tenant
        self._users.setdefault(tenant_id, [])
        return tenant

    def get_tenant(self, tenant_id: str) -> Tenant | None:
        return self._tenants.get(tenant_id)

    def add_user(self, tenant_id: str, user_id: str) -> bool:
        if tenant_id not in self._tenants:
            return False
        users = self._users.setdefault(tenant_id, [])
        if user_id not in users:
            users.append(user_id)
        return True

    def get_users(self, tenant_id: str) -> list[str]:
        return list(self._users.get(tenant_id, []))

    def list_tenants(self) -> list[Tenant]:
        return list(self._tenants.values())

    def to_dict(self) -> dict:
        return {
            "tenants": [t.to_dict() for t in self._tenants.values()],
            "count": len(self._tenants),
        }
