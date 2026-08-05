"""LinkedIn Auth — OAuth token management (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_SCOPES = ["r_liteprofile", "w_member_social"]


class LinkedInAuth:
    """Manage LinkedIn OAuth tokens and auth state."""

    def __init__(self) -> None:
        self._token = ""
        self._scopes = list(_SCOPES)

    def set_token(self, *, token: str = "") -> dict:
        self._token = token or ""
        return {"authorized": bool(self._token), "scopes": self._scopes}

    def refresh_url(self, *, redirect_uri: str = "") -> str:
        """Build an authorization URL for the OAuth flow."""
        from urllib.parse import urlencode

        params = {
            "response_type": "code",
            "client_id": "your_client_id",
            "redirect_uri": redirect_uri or "https://localhost/callback",
            "scope": " ".join(self._scopes),
        }
        return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"

    @property
    def authorized(self) -> bool:
        return bool(self._token)

    def stats(self) -> dict[str, int]:
        return {"scopes": len(self._scopes)}


_AUTH: LinkedInAuth | None = None


def get_linkedin_auth() -> LinkedInAuth:
    """Get the module-level singleton LinkedIn auth."""
    global _AUTH
    if _AUTH is None:
        _AUTH = LinkedInAuth()
    return _AUTH
