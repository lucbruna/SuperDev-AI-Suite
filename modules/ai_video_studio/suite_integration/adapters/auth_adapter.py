"""Auth adapter — reuse the platform JWT manager for token verification.

Bridges to ``backend.auth.jwt`` (the suite backend's JWT manager), so the
studio never re-implements token verification. Missing tokens and
platform-unavailable states answer safely instead of raising.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.suite_integration.adapters.base import (
    SuiteAdapter,
    ensure_suite_importable,
)


class AuthAdapter(SuiteAdapter):
    """Token verification through the suite backend JWT manager."""

    name = "auth"
    description = "Reuse the platform JWT manager (backend.auth.jwt) for token verification"
    platform_module = "backend.auth.jwt"
    actions = ("verify_token",)

    async def verify_token(self, token: str | None) -> dict[str, Any]:
        """Verify a bearer token; answers ``{ok, user_id?, reason?}``."""
        if not token:
            return {"ok": False, "reason": "missing_token", "platform": self.available()}
        ensure_suite_importable()
        if not self.available():
            return {"ok": False, "reason": "platform_unavailable", "platform": False}
        try:
            from backend.auth.jwt import get_jwt_manager

            payload = await get_jwt_manager().verify_token(token)
            if not payload:
                return {"ok": False, "reason": "invalid_or_expired", "platform": True}
            return {
                "ok": True,
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "platform": True,
            }
        except Exception as e:  # noqa: BLE001 — token verification must not raise
            self._error = f"verify failed: {e}"
            return {"ok": False, "reason": self._error, "platform": True}
