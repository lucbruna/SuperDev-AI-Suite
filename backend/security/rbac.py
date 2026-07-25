from __future__ import annotations

from enum import Enum
from functools import wraps
from typing import Callable

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.role import Role, user_roles, role_permissions
from backend.database.models.permission import Permission


class Resource(str, Enum):
    USER = "user"
    PROJECT = "project"
    WORKFLOW = "workflow"
    AGENT = "agent"
    PLUGIN = "plugin"
    PROVIDER = "provider"
    RUNTIME = "runtime"
    ORGANIZATION = "organization"
    ADMIN = "admin"


class Action(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    ADMIN = "admin"


class RBACEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_permission(self, user_id: str, resource: Resource, action: Action) -> bool:
        query = (
            select(Permission)
            .join(role_permissions, Permission.id == role_permissions.c.permission_id)
            .join(Role, Role.id == role_permissions.c.role_id)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id)
            .where(Permission.resource == resource.value)
            .where(Permission.action == action.value)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_user_roles(self, user_id: str) -> list[str]:
        query = (
            select(Role.name)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id)
        )
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def get_user_permissions(self, user_id: str) -> list[str]:
        query = (
            select(Permission.name)
            .join(role_permissions, Permission.id == role_permissions.c.permission_id)
            .join(Role, Role.id == role_permissions.c.role_id)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id)
        )
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def assign_role(self, user_id: str, role_id: str) -> None:
        from backend.utils.uuid_utils import generate_uuid
        from sqlalchemy import insert

        await self.db.execute(
            insert(user_roles).values(user_id=user_id, role_id=role_id)
        )
        await self.db.commit()

    async def remove_role(self, user_id: str, role_id: str) -> None:
        from sqlalchemy import delete

        await self.db.execute(
            delete(user_roles)
            .where(user_roles.c.user_id == user_id)
            .where(user_roles.c.role_id == role_id)
        )
        await self.db.commit()


def require_permission(resource: Resource, action: Action):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, db: AsyncSession, current_user, **kwargs):
            engine = RBACEngine(db)
            if not await engine.check_permission(str(current_user.id), resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {resource.value}:{action.value} required",
                )
            return await func(*args, db=db, current_user=current_user, **kwargs)
        return wrapper
    return decorator
