"""Authentication API routes with security hardening.

Features:
- Account lockout after 5 failed attempts (15min)
- Token blacklist checking on refresh
- Logout with token revocation
- JTI in all tokens
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import get_jwt_manager
from backend.auth.passwords import verify_password
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.middleware.auth_rate_limit import login_limiter
from backend.middleware.authentication import account_lockout
from backend.users.service import UserService

router = APIRouter()

# ------------------------------------------------------------------
# Request/Response models
# ------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str
    full_name: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{" + str(_PASSWORD_MIN_LENGTH) + r",}$"
)


def _validate_password_strength(password: str) -> None:
    """Validate password meets security requirements."""
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {_PASSWORD_MIN_LENGTH} characters",
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter",
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter",
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one digit",
        )
    if not re.search(r"[@$!%*?&#]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one special character (@$!%*?&#)",
        )


def _validate_email(email: str) -> None:
    """Basic email format validation."""
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )


# ------------------------------------------------------------------
# Auth endpoints
# ------------------------------------------------------------------


@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(login_limiter),
) -> dict[str, Any]:
    """Authenticate user with email/password.

    Features:
    - Account lockout after 5 failed attempts (15min)
    - Rate limiting per IP
    - JTI in tokens for revocation
    """
    _validate_email(request.email)

    # Check account lockout
    if account_lockout.is_locked(request.email):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked due to too many failed attempts. Try again in 15 minutes.",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(request.email)

    if not user or not verify_password(request.password, user.hashed_password):
        # Record failed attempt
        is_locked = account_lockout.record_failure(request.email)
        if is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account locked due to too many failed attempts. Try again in 15 minutes.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Successful login — clear failures
    account_lockout.clear_failures(request.email)

    # Create tokens with JTI
    manager = get_jwt_manager()
    tokens = manager.create_token_pair(subject=str(user.id))

    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": getattr(user, "username", user.email.split("@")[0]),
                "fullName": getattr(user, "full_name", ""),
                "avatarUrl": getattr(user, "avatar_url", ""),
                "role": getattr(user, "role", "user"),
                "isEmailVerified": getattr(user, "is_verified", False),
                "createdAt": getattr(user, "created_at", datetime.now(UTC)).isoformat()
                if hasattr(user, "created_at")
                else datetime.now(UTC).isoformat(),
                "updatedAt": getattr(user, "updated_at", datetime.now(UTC)).isoformat()
                if hasattr(user, "updated_at")
                else datetime.now(UTC).isoformat(),
            },
            "accessToken": tokens["access_token"],
            "refreshToken": tokens["refresh_token"],
            "expiresIn": int(tokens["expires_in"]),
        },
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(login_limiter),
) -> dict[str, Any]:
    """Register new user with password strength validation."""
    _validate_email(request.email)
    _validate_password_strength(request.password)

    user_service = UserService(db)
    existing = await user_service.get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check username uniqueness
    existing_username = await user_service.get_user_by_username(request.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = await user_service.create_user(
        email=request.email,
        password=request.password,
        username=request.username,
        full_name=request.full_name,
    )

    manager = get_jwt_manager()
    tokens = manager.create_token_pair(subject=str(user.id))

    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": getattr(user, "username", user.email.split("@")[0]),
                "fullName": getattr(user, "full_name", ""),
                "avatarUrl": getattr(user, "avatar_url", ""),
                "role": getattr(user, "role", "user"),
                "isEmailVerified": getattr(user, "is_verified", False),
                "createdAt": getattr(user, "created_at", datetime.now(UTC)).isoformat()
                if hasattr(user, "created_at")
                else datetime.now(UTC).isoformat(),
                "updatedAt": getattr(user, "updated_at", datetime.now(UTC)).isoformat()
                if hasattr(user, "updated_at")
                else datetime.now(UTC).isoformat(),
            },
            "accessToken": tokens["access_token"],
            "refreshToken": tokens["refresh_token"],
            "expiresIn": int(tokens["expires_in"]),
        },
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token.

    Validates refresh token type and blacklist status.
    Old refresh token is NOT revoked (rotation not enforced for UX).
    """
    manager = get_jwt_manager()
    payload = await manager.verify_refresh_token(request.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Check if all user tokens are revoked
    if await manager.is_user_revoked(subject):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    tokens = manager.create_token_pair(subject=subject)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, str]:
    """Logout by revoking the refresh token.

    Optionally revoke all user tokens.
    """
    manager = get_jwt_manager()

    if request.refresh_token:
        await manager.revoke_token(request.refresh_token)

    return {"success": True, "message": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, str | bool]:
    """Revoke ALL tokens for the current user."""
    manager = get_jwt_manager()
    await manager.revoke_all_user_tokens(current_user["id"])
    return {"success": True, "message": "All sessions revoked"}


@router.get("/me")
async def get_current_user_profile(
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get current user profile."""
    service = UserService(db)
    user = await service.get_user(current_user["id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": getattr(user, "username", ""),
                "fullName": getattr(user, "full_name", ""),
                "avatarUrl": getattr(user, "avatar_url", ""),
                "role": getattr(user, "role", "user"),
                "isEmailVerified": getattr(user, "is_verified", False),
                "createdAt": str(user.created_at) if hasattr(user, "created_at") else "",
                "updatedAt": str(user.updated_at) if hasattr(user, "updated_at") else "",
            }
        },
    }
