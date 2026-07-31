"""Unified authentication middleware and dependencies.

This module provides:
- AuthMiddleware for global request authentication
- get_current_user dependency with blacklist checking
- Account lockout protection
- Logout with token revocation
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import get_jwt_manager
from backend.database.session import get_db
from backend.users.repository import UserRepository

security = HTTPBearer(auto_error=False)

# ------------------------------------------------------------------
# Account lockout protection
# ------------------------------------------------------------------

_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_DURATION_SECONDS = 900  # 15 minutes


class AccountLockout:
    """In-memory account lockout tracker.

    In production, use Redis for distributed lockout across workers.
    """

    def __init__(self):
        self._failures: dict[str, list[float]] = defaultdict(list)
        self._locked_until: dict[str, float] = {}

    def record_failure(self, email: str) -> bool:
        """Record a failed login attempt. Returns True if account is now locked."""
        now = time.time()

        # Check if already locked
        if email in self._locked_until:
            if now < self._locked_until[email]:
                return True
            else:
                # Lockout expired
                del self._locked_until[email]
                self._failures[email] = []

        # Clean old failures
        self._failures[email] = [t for t in self._failures[email] if now - t < _LOCKOUT_DURATION_SECONDS]
        self._failures[email].append(now)

        # Check if should lock
        if len(self._failures[email]) >= _MAX_FAILED_ATTEMPTS:
            self._locked_until[email] = now + _LOCKOUT_DURATION_SECONDS
            return True
        return False

    def is_locked(self, email: str) -> bool:
        """Check if an account is currently locked."""
        if email not in self._locked_until:
            return False
        if time.time() < self._locked_until[email]:
            return True
        # Lockout expired
        del self._locked_until[email]
        self._failures.pop(email, None)
        return False

    def clear_failures(self, email: str) -> None:
        """Clear failures on successful login."""
        self._failures.pop(email, None)
        self._locked_until.pop(email, None)


account_lockout = AccountLockout()

# ------------------------------------------------------------------
# Authentication middleware
# ------------------------------------------------------------------


class AuthMiddleware:
    """Global auth middleware that validates JWT on all non-excluded paths.

    Sets request.state.user_id and request.state.token_payload
    for downstream use.
    """

    def __init__(self, excluded_paths: list[str] | None = None) -> None:
        self.excluded_paths = excluded_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/health",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def __call__(self, request: Request, call_next: Any) -> Any:
        from starlette.responses import JSONResponse

        path = request.url.path

        # Skip excluded paths
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return await call_next(request)

        # Skip WebSocket (handled separately)
        if request.scope.get("type") == "websocket":
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
            )

        token = auth_header.removeprefix("Bearer ")
        manager = get_jwt_manager()
        payload = await manager.verify_token(token)

        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        # Check if all user tokens are revoked
        user_id = payload.get("sub")
        if user_id and await manager.is_user_revoked(user_id):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has been revoked"},
            )

        request.state.user_id = user_id
        request.state.token_payload = payload
        return await call_next(request)


# ------------------------------------------------------------------
# FastAPI dependencies
# ------------------------------------------------------------------


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Dependency that returns the current authenticated user dict.

    Checks JWT validity, blacklist, and user existence.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    manager = get_jwt_manager()
    payload = await manager.verify_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Check if all user tokens are revoked
    if await manager.is_user_revoked(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    # Verify user exists and is active
    repository = UserRepository(db)
    user = await repository.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "is_superuser": getattr(user, "is_superuser", False),
        "payload": payload,
    }


async def get_current_active_user(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Dependency that ensures the current user is active."""
    if current_user.get("payload", {}).get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return current_user
