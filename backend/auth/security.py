"""Password hashing and legacy token utilities.

DEPRECATED: The token functions here are kept for backward compatibility.
New code should use backend.auth.jwt.JWTManager directly.
"""

from __future__ import annotations

from datetime import timedelta

from passlib.context import CryptContext

# ------------------------------------------------------------------
# Password hashing (single source of truth)
# ------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt."""
    return pwd_context.hash(password)


# ------------------------------------------------------------------
# Legacy token functions — DEPRECATED, use JWTManager instead
# ------------------------------------------------------------------


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """DEPRECATED: Use JWTManager.create_access_token() instead."""
    from backend.auth.jwt import get_jwt_manager

    manager = get_jwt_manager()
    subject = data.get("sub", "")
    return manager.create_access_token(subject, expires_delta)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """DEPRECATED: Use JWTManager.create_refresh_token() instead."""
    from backend.auth.jwt import get_jwt_manager

    manager = get_jwt_manager()
    subject = data.get("sub", "")
    return manager.create_refresh_token(subject, expires_delta)


def decode_token(token: str) -> dict | None:
    """DEPRECATED: Use JWTManager.decode_token() instead."""
    from backend.auth.jwt import get_jwt_manager

    manager = get_jwt_manager()
    return manager.decode_token(token)
