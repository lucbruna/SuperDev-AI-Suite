from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import JWTManager
from backend.config import config
from backend.database.session import get_db as _get_db_session
from backend.exceptions import (
    AuthenticationException,
    AuthorizationException,
)

security_scheme = HTTPBearer(auto_error=False)


async def get_jwt_manager() -> JWTManager:
    return JWTManager(secret_key=str(config.auth.secret_key))


async def get_redis() -> AsyncGenerator[Any, None]:
    redis_instance = None
    try:
        from redis.asyncio import Redis

        redis_instance = Redis(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password or None,
            db=config.redis.db,
            decode_responses=config.redis.decode_responses,
            socket_connect_timeout=config.redis.socket_connect_timeout,
            socket_keepalive=config.redis.socket_keepalive,
            health_check_interval=config.redis.health_check_interval,
        )
        yield redis_instance
    finally:
        if redis_instance is not None:
            await redis_instance.aclose()


get_db = _get_db_session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> dict[str, Any]:
    if credentials is None:
        raise AuthenticationException("Missing authentication credentials")

    token = credentials.credentials
    if not token:
        raise AuthenticationException("Invalid token")

    from jose import JWTError, jwt

    try:
        payload = jwt.decode(
            token,
            config.auth.secret_key,
            algorithms=[config.auth.algorithm],
            audience=config.auth.audience,
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise AuthenticationException("Invalid token payload")
        return {"id": user_id, "roles": payload.get("roles", []), "payload": payload}
    except JWTError:
        raise AuthenticationException("Invalid or expired token")


async def get_current_active_user(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    payload = current_user.get("payload", {})
    if payload.get("disabled", False):
        raise AuthenticationException("User account is disabled")
    return current_user


async def get_current_admin_user(
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    from backend.users.service import UserService

    service = UserService(db)
    user = await service.get_user(current_user["id"])
    if not user or not getattr(user, "is_superuser", False):
        raise AuthorizationException("Admin privileges required")
    return current_user
