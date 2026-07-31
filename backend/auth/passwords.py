"""Password hashing — single source of truth.

All password hashing/verification across the codebase should import from here.
Uses bcrypt directly (passlib is incompatible with bcrypt>=4.1).
"""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)
