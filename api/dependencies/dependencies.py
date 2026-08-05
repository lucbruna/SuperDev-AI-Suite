from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.auth import decode_access_token
from core.configuration import Settings, settings
from core.event_bus import EventBus
from core.orchestrator import Orchestrator
from enterprise.security.audit import AuditManager
from enterprise.security.permissions import PermissionManager
from enterprise.security.users import User, UserManager

_security_scheme = HTTPBearer(auto_error=False)

_event_bus_instance: EventBus | None = None
_user_manager_instance: UserManager | None = None
_permission_manager_instance: PermissionManager | None = None
_audit_manager_instance: AuditManager | None = None
_orchestrator_instance: Orchestrator | None = None


def get_settings() -> Settings:
    return settings


async def get_event_bus() -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus(use_rabbitmq=False)
        await _event_bus_instance.start()
    return _event_bus_instance


async def get_user_manager() -> UserManager:
    global _user_manager_instance
    if _user_manager_instance is None:
        bus = await get_event_bus()
        _user_manager_instance = UserManager(event_bus=bus)
        perm = await get_permission_manager()
        for user in _user_manager_instance._users.values():
            if user.is_superuser or user.role == "administrator":
                admin_role = next(
                    (r for r in perm._roles.values() if r.name.lower() == "administrator"),
                    None,
                )
                if admin_role:
                    perm.assign_role(user.id, admin_role.id)
    return _user_manager_instance


async def get_permission_manager() -> PermissionManager:
    global _permission_manager_instance
    if _permission_manager_instance is None:
        bus = await get_event_bus()
        _permission_manager_instance = PermissionManager(event_bus=bus)
    return _permission_manager_instance


async def get_audit_manager() -> AuditManager:
    global _audit_manager_instance
    if _audit_manager_instance is None:
        bus = await get_event_bus()
        _audit_manager_instance = AuditManager(event_bus=bus)
    return _audit_manager_instance


async def get_orchestrator() -> Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_security_scheme),
    user_manager: UserManager = Depends(get_user_manager),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = user_manager.get_user(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    request.state.user = user
    return user


def require_permission(permission: str) -> Callable[[User, PermissionManager], None]:
    def _check(
        current_user: User = Depends(get_current_user),
        perm_manager: PermissionManager = Depends(get_permission_manager),
    ) -> None:
        if not current_user.is_superuser and not perm_manager.check_permission(
            current_user.id, permission
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}",
            )
    return _check
