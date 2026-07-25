from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.permission import Permission
from backend.database.models.role import Role
from backend.utils.uuid_utils import generate_uuid

DEFAULT_ROLES = [
    {"name": "super_admin", "description": "Super administrator with full access", "is_system": True},
    {"name": "admin", "description": "Administrator with most access", "is_system": True},
    {"name": "developer", "description": "Developer with project access", "is_system": True},
    {"name": "viewer", "description": "Read-only access", "is_system": True},
]

DEFAULT_PERMISSIONS = [
    {"name": "users:read", "resource": "user", "action": "read"},
    {"name": "users:write", "resource": "user", "action": "write"},
    {"name": "users:delete", "resource": "user", "action": "delete"},
    {"name": "projects:read", "resource": "project", "action": "read"},
    {"name": "projects:write", "resource": "project", "action": "write"},
    {"name": "projects:delete", "resource": "project", "action": "delete"},
    {"name": "workflows:read", "resource": "workflow", "action": "read"},
    {"name": "workflows:write", "resource": "workflow", "action": "write"},
    {"name": "workflows:execute", "resource": "workflow", "action": "execute"},
    {"name": "agents:read", "resource": "agent", "action": "read"},
    {"name": "agents:write", "resource": "agent", "action": "write"},
    {"name": "agents:execute", "resource": "agent", "action": "execute"},
    {"name": "plugins:read", "resource": "plugin", "action": "read"},
    {"name": "plugins:write", "resource": "plugin", "action": "write"},
    {"name": "plugins:install", "resource": "plugin", "action": "manage"},
    {"name": "providers:read", "resource": "provider", "action": "read"},
    {"name": "providers:write", "resource": "provider", "action": "write"},
    {"name": "admin:manage", "resource": "admin", "action": "admin"},
]

ROLE_PERMISSION_MAP = {
    "super_admin": [p["name"] for p in DEFAULT_PERMISSIONS],
    "admin": [p["name"] for p in DEFAULT_PERMISSIONS if p["name"] != "admin:manage"],
    "developer": [
        "users:read", "projects:read", "projects:write",
        "workflows:read", "workflows:write", "workflows:execute",
        "agents:read", "agents:write", "agents:execute",
        "plugins:read", "providers:read",
    ],
    "viewer": [
        "users:read", "projects:read", "workflows:read",
        "agents:read", "plugins:read", "providers:read",
    ],
}


async def seed_roles_and_permissions(db: AsyncSession) -> None:
    from backend.database.models.role import role_permissions

    existing = await db.execute(select(Role).limit(1))
    if existing.scalar_one_or_none():
        return

    permission_map = {}
    for perm_data in DEFAULT_PERMISSIONS:
        perm = Permission(
            id=generate_uuid(),
            name=perm_data["name"],
            resource=perm_data["resource"],
            action=perm_data["action"],
        )
        db.add(perm)
        permission_map[perm_data["name"]] = perm

    await db.flush()

    for role_data in DEFAULT_ROLES:
        role = Role(
            id=generate_uuid(),
            name=role_data["name"],
            description=role_data["description"],
            is_system=role_data["is_system"],
        )
        db.add(role)
        await db.flush()

        perm_names = ROLE_PERMISSION_MAP.get(role_data["name"], [])
        for perm_name in perm_names:
            if perm_name in permission_map:
                await db.execute(
                    role_permissions.insert().values(
                        role_id=role.id,
                        permission_id=permission_map[perm_name].id,
                    )
                )

    await db.commit()
