"""Role-Based Access Control (RBAC) module.

Provides role definitions, permission checking, and FastAPI dependency
factories for enforcing authorization across the application.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.deps import get_current_user
from backend.database.models.role import Permission, Role, UserRole, role_permissions
from backend.database.models.user import User

# ---------------------------------------------------------------------------
# System constants
# ---------------------------------------------------------------------------

class RoleName(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"


class Resource(StrEnum):
    USERS = "users"
    PROJECTS = "projects"
    WORKFLOWS = "workflows"
    AGENTS = "agents"
    PLUGINS = "plugins"
    PROVIDERS = "providers"
    KNOWLEDGE = "knowledge"
    ORGANIZATIONS = "organizations"
    AUDIT = "audit"
    NOTIFICATIONS = "notifications"
    SETTINGS = "settings"


class Action(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    ADMIN = "admin"


# ---------------------------------------------------------------------------
# Default role -> permission mapping
# ---------------------------------------------------------------------------

_ALL_RESOURCES = [r.value for r in Resource]
_ALL_ACTIONS = [a.value for a in Action]

_DEFAULT_ROLE_PERMISSIONS: dict[RoleName, set[tuple[str, str]]] = {
    RoleName.SUPER_ADMIN: {(r, a) for r in _ALL_RESOURCES for a in _ALL_ACTIONS},
    RoleName.ADMIN: {
        *{(r, a) for r in _ALL_RESOURCES for a in (Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE)},
        ("users", "admin"),
        ("organizations", "admin"),
    },
    RoleName.MANAGER: {
        *{(r, Action.READ) for r in _ALL_RESOURCES},
        ("projects", Action.CREATE), ("projects", Action.UPDATE), ("projects", Action.DELETE),
        ("workflows", Action.CREATE), ("workflows", Action.UPDATE), ("workflows", Action.EXECUTE),
        ("agents", Action.CREATE), ("agents", Action.UPDATE),
        ("knowledge", Action.CREATE), ("knowledge", Action.UPDATE),
        ("plugins", Action.READ),
        ("providers", Action.READ),
        ("notifications", Action.READ), ("notifications", Action.UPDATE),
    },
    RoleName.DEVELOPER: {
        *{(r, Action.READ) for r in _ALL_RESOURCES},
        ("projects", Action.CREATE), ("projects", Action.UPDATE),
        ("workflows", Action.CREATE), ("workflows", Action.UPDATE), ("workflows", Action.EXECUTE),
        ("agents", Action.CREATE), ("agents", Action.UPDATE),
        ("knowledge", Action.CREATE), ("knowledge", Action.UPDATE),
        ("plugins", Action.READ),
        ("providers", Action.READ),
        ("notifications", Action.READ),
    },
    RoleName.VIEWER: {(r, Action.READ) for r in _ALL_RESOURCES},
    RoleName.GUEST: {
        ("projects", Action.READ),
        ("workflows", Action.READ),
        ("knowledge", Action.READ),
    },
}


# ---------------------------------------------------------------------------
# PermissionChecker
# ---------------------------------------------------------------------------

class PermissionChecker:
    """Check whether a user holds a specific permission via any of their roles."""

    def __init__(self, resource: Resource | str, action: Action | str) -> None:
        self.resource = resource.value if isinstance(resource, Resource) else resource
        self.action = action.value if isinstance(action, Action) else action

    async def check(
        self,
        session: AsyncSession,
        user_id: str,
        organization_id: str | None = None,
    ) -> bool:
        """Return *True* if *user_id* has ``(resource, action)`` permission.

        Superusers always pass.  Expired ``UserRole`` entries are skipped.
        """
        # Load user to check superuser flag
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user is None:
            return False
        if user.is_superuser:
            return True

        # Query through UserRole -> Role -> Permission via association table
        now = datetime.now(UTC)
        stmt = (
            select(Permission.id)
            .join(role_permissions, Permission.id == role_permissions.c.permission_id)
            .join(Role, Role.id == role_permissions.c.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Permission.resource == self.resource,
                    Permission.action == self.action,
                    (UserRole.expires_at.is_(None)) | (UserRole.expires_at > now),
                )
            )
            .limit(1)
        )

        # Filter by organization if provided
        if organization_id is not None:
            stmt = stmt.where(
                (UserRole.organization_id.is_(None))
                | (UserRole.organization_id == organization_id)
            )

        result = await session.execute(stmt)
        return result.first() is not None


# ---------------------------------------------------------------------------
# FastAPI dependency factory
# ---------------------------------------------------------------------------

def require_permission(
    resource: Resource | str,
    action: Action | str,
    use_organization: bool = True,
) -> Callable:
    """Return a FastAPI dependency that enforces a single permission.

    The dependency returns the authenticated ``User`` object on success
    and raises *403 Forbidden* when the permission check fails.

    Parameters
    ----------
    resource:
        The resource type to check against.
    action:
        The action to check against.
    use_organization:
        When *True* (default) the dependency extracts ``organization_id``
        from query parameters if present.
    """
    checker = PermissionChecker(resource, action)

    async def _dependency(
        request: Request,
        user_id: str = Depends(get_current_user),
    ) -> User:
        # Extract organization_id from query if enabled
        organization_id: str | None = None
        if use_organization:
            organization_id = request.query_params.get("organization_id")

        # Get the DB session from app state (set by middleware)
        session: AsyncSession = request.state.db_session

        # Load full user object
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        allowed = await checker.check(session, str(user.id), organization_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {resource} {action}",
            )
        return user

    return _dependency


# ---------------------------------------------------------------------------
# Database seeding helpers
# ---------------------------------------------------------------------------

async def ensure_system_roles(session: AsyncSession) -> None:
    """Create system roles and permissions if they do not already exist.

    This function is idempotent — safe to call on every startup.
    """
    for role_name in RoleName:
        existing = await session.execute(
            select(Role).where(Role.name == role_name.value)
        )
        if existing.scalar_one_or_none() is not None:
            continue

        role = Role(
            name=role_name.value,
            description=f"System role: {role_name.value}",
            is_system=True,
        )
        session.add(role)
        await session.flush()

        # Attach default permissions
        perm_tuples = _DEFAULT_ROLE_PERMISSIONS.get(role_name, set())
        for res, act in perm_tuples:
            perm_result = await session.execute(
                select(Permission).where(
                    and_(Permission.resource == res, Permission.action == act)
                )
            )
            perm = perm_result.scalar_one_or_none()
            if perm is None:
                perm = Permission(
                    name=f"{res}:{act}",
                    resource=res,
                    action=act,
                    is_system=True,
                )
                session.add(perm)
                await session.flush()
            role.permissions.append(perm)

    await session.commit()


async def assign_role(
    session: AsyncSession,
    user_id: str,
    role_name: RoleName | str,
    organization_id: str | None = None,
    project_id: str | None = None,
    expires_at: datetime | None = None,
) -> UserRole:
    """Assign a role to a user.  Raises ``ValueError`` if the role does not exist.

    Duplicate assignments are silently skipped.
    """
    name = role_name.value if isinstance(role_name, RoleName) else role_name
    role_result = await session.execute(select(Role).where(Role.name == name))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise ValueError(f"Role '{name}' does not exist")

    # Check for duplicate
    dup = await session.execute(
        select(UserRole).where(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id,
                UserRole.organization_id == organization_id,
                UserRole.project_id == project_id,
            )
        )
    )
    existing = dup.scalar_one_or_none()
    if existing is not None:
        return existing

    ur = UserRole(
        user_id=user_id,
        role_id=role.id,
        organization_id=organization_id,
        project_id=project_id,
        expires_at=expires_at,
    )
    session.add(ur)
    await session.flush()
    return ur


async def get_user_permissions(
    session: AsyncSession,
    user_id: str,
    organization_id: str | None = None,
) -> set[tuple[str, str]]:
    """Return the effective permission set ``(resource, action)`` for a user."""
    now = datetime.now(UTC)
    stmt = (
        select(Permission.resource, Permission.action)
        .join(role_permissions, Permission.id == role_permissions.c.permission_id)
        .join(Role, Role.id == role_permissions.c.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(
            and_(
                UserRole.user_id == user_id,
                (UserRole.expires_at.is_(None)) | (UserRole.expires_at > now),
            )
        )
        .distinct()
    )
    if organization_id is not None:
        stmt = stmt.where(
            (UserRole.organization_id.is_(None))
            | (UserRole.organization_id == organization_id)
        )
    result = await session.execute(stmt)
    return {(row[0], row[1]) for row in result.all()}
