"""YouTube Auth — OAuth token lifecycle state machine (Volume 7)."""
from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class YoutubeAuth:
    """OAuth2 flow state machine: pending → authorized → expired → refreshed."""

    def __init__(self) -> None:
        self._state = "idle"
        self._token: str | None = None
        self._expires_at: float | None = None
        self._refresh_token: str | None = None

    @property
    def state(self) -> str:
        if self._token and self._expires_at and time.time() > self._expires_at:
            return "expired"
        return self._state

    def start(self) -> dict:
        """Begin the OAuth flow (returns the authorization step)."""
        self._state = "pending"
        return {"state": self._state, "step": "authorization_url_required"}

    def complete(self, *, token: str, expires_in: int = 3600, refresh_token: str | None = None) -> dict:
        """Complete the flow with the exchanged token."""
        self._token = token
        self._expires_at = time.time() + max(60, expires_in)
        self._refresh_token = refresh_token
        self._state = "authorized"
        return {"state": self._state, "expires_in": expires_in}

    def refresh(self) -> dict:
        """Simulate a token refresh (real call plugs in here)."""
        if not self._refresh_token:
            return {"success": False, "error": "No refresh token available"}
        self._token = f"refreshed_{int(time.time())}"
        self._expires_at = time.time() + 3600
        return {"success": True, "state": "authorized", "expires_at": self._expires_at}

    def revoke(self) -> dict:
        self._token = None
        self._refresh_token = None
        self._state = "idle"
        return {"state": self._state}

    def stats(self) -> dict[str, str]:
        return {"state": self.state, "token_present": str(bool(self._token))}


_AUTH: YoutubeAuth | None = None


def get_youtube_auth() -> YoutubeAuth:
    """Get the module-level singleton YouTube auth manager."""
    global _AUTH
    if _AUTH is None:
        _AUTH = YoutubeAuth()
    return _AUTH
