"""Authentication Bridge — delegates token verification to the suite platform."""
from __future__ import annotations

from typing import Any


class AuthenticationBridge:
    """Token verification via the suite JWT manager (Volume 10 suite bridge)."""

    async def verify_token(self, token: str | None) -> dict[str, Any]:
        try:
            from modules.ai_video_studio.suite_integration import get_suite_bridge

            return await get_suite_bridge().verify_token(token)
        except Exception as e:  # noqa: BLE001 — never raise from the bridge
            return {"ok": False, "reason": f"bridge unavailable: {e}", "platform": False}


_authentication_bridge: AuthenticationBridge | None = None


def get_authentication_bridge() -> AuthenticationBridge:
    global _authentication_bridge
    if _authentication_bridge is None:
        _authentication_bridge = AuthenticationBridge()
    return _authentication_bridge
