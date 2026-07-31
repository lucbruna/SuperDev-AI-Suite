"""
Seed de roles e permissões.
Usa session sync (sqlalchemy.orm.Session) para compatibilidade com seed_data.py.
"""

from __future__ import annotations

from typing import Any

from backend.database.models.role import Permission, Role, role_permissions
from sqlalchemy import select

# ── UUIDs determinísticos ─────────────────────────────────────────

ROLE_IDS = {
    "super_admin": "00000000-0000-0000-0000-000000000100",
    "admin": "00000000-0000-0000-0000-000000000101",
    "developer": "00000000-0000-0000-0000-000000000102",
    "viewer": "00000000-0000-0000-0000-000000000103",
}

PERM_IDS = {
    "users:read": "00000000-0000-0000-0000-000000000200",
    "users:write": "00000000-0000-0000-0000-000000000201",
    "users:delete": "00000000-0000-0000-0000-000000000202",
    "projects:read": "00000000-0000-0000-0000-000000000210",
    "projects:write": "00000000-0000-0000-0000-000000000211",
    "projects:delete": "00000000-0000-0000-0000-000000000212",
    "workflows:read": "00000000-0000-0000-0000-000000000220",
    "workflows:write": "00000000-0000-0000-0000-000000000221",
    "workflows:execute": "00000000-0000-0000-0000-000000000222",
    "agents:read": "00000000-0000-0000-0000-000000000230",
    "agents:write": "00000000-0000-0000-0000-000000000231",
    "agents:execute": "00000000-0000-0000-0000-000000000232",
    "plugins:read": "00000000-0000-0000-0000-000000000240",
    "plugins:write": "00000000-0000-0000-0000-000000000241",
    "plugins:install": "00000000-0000-0000-0000-000000000242",
    "providers:read": "00000000-0000-0000-0000-000000000250",
    "providers:write": "00000000-0000-0000-0000-000000000251",
    "admin:manage": "00000000-0000-0000-0000-000000000260",
}

DEFAULT_ROLES: list[dict[str, Any]] = [
    {"id": ROLE_IDS["super_admin"], "name": "super_admin", "description": "Super administrator with full access", "is_system": True},
    {"id": ROLE_IDS["admin"], "name": "admin", "description": "Administrator with most access", "is_system": True},
    {"id": ROLE_IDS["developer"], "name": "developer", "description": "Developer with project access", "is_system": True},
    {"id": ROLE_IDS["viewer"], "name": "viewer", "description": "Read-only access", "is_system": True},
]

DEFAULT_PERMISSIONS: list[dict[str, Any]] = [
    {"id": PERM_IDS["users:read"], "name": "users:read", "resource": "user", "action": "read"},
    {"id": PERM_IDS["users:write"], "name": "users:write", "resource": "user", "action": "write"},
    {"id": PERM_IDS["users:delete"], "name": "users:delete", "resource": "user", "action": "delete"},
    {"id": PERM_IDS["projects:read"], "name": "projects:read", "resource": "project", "action": "read"},
    {"id": PERM_IDS["projects:write"], "name": "projects:write", "resource": "project", "action": "write"},
    {"id": PERM_IDS["projects:delete"], "name": "projects:delete", "resource": "project", "action": "delete"},
    {"id": PERM_IDS["workflows:read"], "name": "workflows:read", "resource": "workflow", "action": "read"},
    {"id": PERM_IDS["workflows:write"], "name": "workflows:write", "resource": "workflow", "action": "write"},
    {"id": PERM_IDS["workflows:execute"], "name": "workflows:execute", "resource": "workflow", "action": "execute"},
    {"id": PERM_IDS["agents:read"], "name": "agents:read", "resource": "agent", "action": "read"},
    {"id": PERM_IDS["agents:write"], "name": "agents:write", "resource": "agent", "action": "write"},
    {"id": PERM_IDS["agents:execute"], "name": "agents:execute", "resource": "agent", "action": "execute"},
    {"id": PERM_IDS["plugins:read"], "name": "plugins:read", "resource": "plugin", "action": "read"},
    {"id": PERM_IDS["plugins:write"], "name": "plugins:write", "resource": "plugin", "action": "write"},
    {"id": PERM_IDS["plugins:install"], "name": "plugins:install", "resource": "plugin", "action": "manage"},
    {"id": PERM_IDS["providers:read"], "name": "providers:read", "resource": "provider", "action": "read"},
    {"id": PERM_IDS["providers:write"], "name": "providers:write", "resource": "provider", "action": "write"},
    {"id": PERM_IDS["admin:manage"], "name": "admin:manage", "resource": "admin", "action": "admin"},
]

ROLE_PERMISSION_MAP: dict[str, list[str]] = {
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


def seed_roles_and_permissions(session: Any) -> None:
    """Popula roles e permissões. Idempotente — só executa se não houver dados."""
    existing = session.execute(select(Role).limit(1)).scalar_one_or_none()
    if existing:
        print("[SKIP] Roles ja existem, pulando seed de permissoes")
        return

    # Inserir permissões
    perm_by_name: dict[str, Permission] = {}
    for perm_data in DEFAULT_PERMISSIONS:
        perm = Permission(**perm_data)
        session.add(perm)
        perm_by_name[perm_data["name"]] = perm

    session.flush()

    # Inserir roles e associar permissões
    for role_data in DEFAULT_ROLES:
        perm_names = ROLE_PERMISSION_MAP.get(role_data["name"], [])
        role = Role(**role_data)
        session.add(role)
        session.flush()

        # Associar permissões via tabela role_permissions
        for perm_name in perm_names:
            if perm_name in perm_by_name:
                session.execute(
                    role_permissions.insert().values(
                        role_id=role.id,
                        permission_id=perm_by_name[perm_name].id,
                    )
                )

    session.commit()
    print(f"[OK] Roles e permissoes: {len(DEFAULT_ROLES)} roles, {len(DEFAULT_PERMISSIONS)} permissoes")
