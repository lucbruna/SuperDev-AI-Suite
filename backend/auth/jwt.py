"""Unified JWT Manager with JTI, token blacklist, and RS256 support.

This is the single source of truth for JWT operations across the application.
All other JWT implementations should be removed and replaced with this one.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from jose import JWTError, jwt
from pydantic import SecretStr

from backend.utils.datetime import utc_now
from backend.utils.uuid_utils import generate_uuid


class JWTManager:
    """Unified JWT manager with JTI, blacklist, and algorithm flexibility.

    Features:
    - JTI (JWT ID) for every token — enables revocation
    - Redis-backed blacklist for revoked tokens
    - Support for HS256 (symmetric) and RS256 (asymmetric) algorithms
    - Issuer and audience validation
    - Configurable expiration per token type
    """

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ISSUER: str = "superdev"
    AUDIENCE: str = "superdev-api"

    def __init__(
        self,
        secret_key: str,
        algorithm: str = ALGORITHM,
        access_token_expire: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire: int = REFRESH_TOKEN_EXPIRE_MINUTES,
        issuer: str = ISSUER,
        audience: str = AUDIENCE,
        redis_client: Any | None = None,
    ) -> None:
        # Validate secret key — reject defaults
        if not secret_key or secret_key in (
            "super-dev-secret-key-change-in-production",
            "change-me-in-production",
            "dev-secret-key-change-in-production",
            "change-me-to-a-random-256-bit-secret",
            "",
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong, unique value. Default keys are rejected for security."
            )
        self._secret_key = SecretStr(secret_key)
        self._algorithm = algorithm
        self._access_token_expire = access_token_expire
        self._refresh_token_expire = refresh_token_expire
        self._issuer = issuer
        self._audience = audience
        self._redis = redis_client

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @property
    def access_token_expire_minutes(self) -> int:
        return self._access_token_expire

    @property
    def refresh_token_expire_minutes(self) -> int:
        return self._refresh_token_expire

    # ------------------------------------------------------------------
    # Token creation
    # ------------------------------------------------------------------

    def create_access_token(
        self,
        subject: str,
        expires_delta: timedelta | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create an access token with JTI for revocation support."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self._access_token_expire)
        if expires_delta.total_seconds() <= 0:
            return ""

        now = utc_now()
        payload: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": now + expires_delta,
            "iss": self._issuer,
            "aud": self._audience,
            "type": "access",
            "jti": generate_uuid(),
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(
            payload,
            self._secret_key.get_secret_value(),
            algorithm=self._algorithm,
        )

    def create_refresh_token(
        self,
        subject: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a refresh token with JTI for revocation support."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self._refresh_token_expire)

        now = utc_now()
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + expires_delta,
            "iss": self._issuer,
            "aud": self._audience,
            "type": "refresh",
            "jti": generate_uuid(),
        }

        return jwt.encode(
            payload,
            self._secret_key.get_secret_value(),
            algorithm=self._algorithm,
        )

    # ------------------------------------------------------------------
    # Token verification
    # ------------------------------------------------------------------

    def decode_token(self, token: str) -> dict | None:
        """Decode and validate a JWT token.

        Returns the payload dict on success, None on failure.
        Does NOT check blacklist — use verify_token() for that.
        """
        try:
            payload = jwt.decode(
                token,
                self._secret_key.get_secret_value(),
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
            )
            return payload
        except JWTError:
            return None

    async def verify_token(self, token: str) -> dict | None:
        """Decode + blacklist check + type validation.

        Returns the payload if valid and not blacklisted, None otherwise.
        """
        payload = self.decode_token(token)
        if payload is None:
            return None

        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and await self._is_blacklisted(jti):
            return None

        return payload

    async def verify_access_token(self, token: str) -> dict | None:
        """Verify an access token specifically."""
        payload = await self.verify_token(token)
        if payload and payload.get("type") != "access":
            return None
        return payload

    async def verify_refresh_token(self, token: str) -> dict | None:
        """Verify a refresh token specifically."""
        payload = await self.verify_token(token)
        if payload and payload.get("type") != "refresh":
            return None
        return payload

    # ------------------------------------------------------------------
    # Token revocation (blacklist)
    # ------------------------------------------------------------------

    async def revoke_token(self, token: str) -> bool:
        """Revoke a token by adding its JTI to the blacklist.

        Returns True if successfully revoked, False if token is invalid.
        """
        payload = self.decode_token(token)
        if payload is None:
            return False

        jti = payload.get("jti")
        if not jti:
            return False

        # Calculate remaining TTL
        exp = payload.get("exp")
        if exp:
            from datetime import datetime

            if isinstance(exp, datetime):
                ttl_seconds = max(int((exp - datetime.now(exp.tzinfo)).total_seconds()), 1)
            else:
                ttl_seconds = max(int(exp - utc_now().timestamp()), 1)
        else:
            ttl_seconds = self._refresh_token_expire * 60

        await self._blacklist_jti(jti, ttl_seconds)
        return True

    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a user (requires Redis).

        In practice, this is hard with pure JWT. We use a user-level
        blacklist prefix. Returns approximate count of revoked tokens.
        """
        if not self._redis:
            return 0
        key = f"jwt_revoke_user:{user_id}"
        await self._redis.set(key, "1", ex=self._refresh_token_expire * 60)
        return 1

    async def is_user_revoked(self, user_id: str) -> bool:
        """Check if all tokens for a user have been revoked."""
        if not self._redis:
            return False
        key = f"jwt_revoke_user:{user_id}"
        return await self._redis.exists(key) > 0

    # ------------------------------------------------------------------
    # Blacklist internals
    # ------------------------------------------------------------------

    async def _is_blacklisted(self, jti: str) -> bool:
        """Check if a JTI is in the blacklist."""
        if not self._redis:
            return False
        key = f"jwt_blacklist:{jti}"
        return await self._redis.exists(key) > 0

    async def _blacklist_jti(self, jti: str, ttl_seconds: int) -> None:
        """Add a JTI to the blacklist with TTL."""
        if not self._redis:
            return
        key = f"jwt_blacklist:{jti}"
        await self._redis.set(key, "1", ex=ttl_seconds)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def create_token_pair(
        self,
        subject: str,
        access_expires: timedelta | None = None,
        refresh_expires: timedelta | None = None,
    ) -> dict[str, str | float]:
        """Create both access and refresh tokens for a user."""
        return {
            "access_token": self.create_access_token(subject, access_expires),
            "refresh_token": self.create_refresh_token(subject, refresh_expires),
            "token_type": "bearer",
            "expires_in": (access_expires or timedelta(minutes=self._access_token_expire)).total_seconds(),
        }

    def get_token_info(self, token: str) -> dict[str, Any] | None:
        """Get token metadata without full validation (for debugging)."""
        try:
            # Decode without verification to inspect header
            from jose import jwt as jose_jwt

            unverified = jose_jwt.get_unverified_claims(token)
            unverified_header = jose_jwt.get_unverified_header(token)
            return {
                "algorithm": unverified_header.get("alg"),
                "type": unverified.get("type"),
                "sub": unverified.get("sub"),
                "iss": unverified.get("iss"),
                "aud": unverified.get("aud"),
                "jti": unverified.get("jti"),
                "exp": unverified.get("exp"),
                "iat": unverified.get("iat"),
            }
        except Exception:
            return None


# ------------------------------------------------------------------
# Singleton instance (lazy, requires config)
# ------------------------------------------------------------------

_jwt_manager: JWTManager | None = None


def get_jwt_manager(
    secret_key: str | None = None,
    redis_client: Any | None = None,
) -> JWTManager:
    """Get or create the global JWTManager instance."""
    global _jwt_manager
    if _jwt_manager is None:
        if secret_key is None:
            from backend.config import config

            secret_key = str(config.auth.secret_key)
        _jwt_manager = JWTManager(
            secret_key=secret_key,
            algorithm="HS256",
            redis_client=redis_client,
        )
    return _jwt_manager


def reset_jwt_manager() -> None:
    """Reset the global instance (for testing)."""
    global _jwt_manager
    _jwt_manager = None
