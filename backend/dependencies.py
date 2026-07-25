from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.config import config
from backend.exceptions import (
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
)

security_scheme = HTTPBearer(auto_error=False)


async def get_redis() -> AsyncGenerator[Any, None]:
    redis = None
    try:
        from redis.asyncio import from_url

        redis = await from_url(config.redis.url, decode_responses=config.redis.decode_responses)
        yield redis
    finally:
        if redis is not None:
            await redis.aclose()


async def get_db() -> AsyncGenerator[Any, None]:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(
        config.database.url,
        pool_size=config.database.pool_size,
        max_overflow=config.database.max_overflow,
        echo=config.database.echo,
        pool_pre_ping=config.database.pool_pre_ping,
        pool_recycle=config.database.pool_recycle,
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await engine.dispose()


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
        payload = jwt.decode(token, config.auth.secret_key, algorithms=[config.auth.algorithm])
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
) -> dict[str, Any]:
    roles: list[str] = current_user.get("roles", [])
    if "admin" not in roles:
        raise AuthorizationException("Admin privileges required")
    return current_user