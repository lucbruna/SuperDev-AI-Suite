"""X Auth — OAuth token management (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]


class XAuth:
    """Manage X (Twitter) OAuth tokens and auth state."""

    def __init__(self) -> None:
        self._token = ""
        self._scopes = list(_SCOPES)

    def set_token(self, *, token: str = "") -> dict:
        self._token = token or ""
        return {"authorized": bool(self._token), "scopes": self._scopes}

    def refresh_url(self, *, redirect_uri: str = "") -> str:
        """Build an authorization URL for the OAuth 2.0 flow."""
        from urllib.parse import urlencode

        params = {
            "response_type": "code",
            "client_id": "your_client_id",
            "redirect_uri": redirect_uri or "https://localhost/callback",
            "scope": " ".join(self._scopes),
            "state": "superdev",
        }
        return f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"

    @property
    def authorized(self) -> bool:
        return bool(self._token)

    def stats(self) -> dict[str, int]:
        return {"scopes": len(self._scopes)}


_AUTH: XAuth | None = None


def get_x_auth() -> XAuth:
    """Get the module-level singleton X auth."""
    global _AUTH
    if _AUTH is None:
        _AUTH = XAuth()
    return _AUTH
