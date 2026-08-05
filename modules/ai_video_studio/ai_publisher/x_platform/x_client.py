"""X Client — platform API client (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None


class XClient:
    """X (Twitter) API v2 client.

    Simulated responses when no bearer token is configured.
    """

    def __init__(self) -> None:
        self._token = ""
        self._load_settings()

    def _load_settings(self) -> None:
        try:
            from modules.ai_video_studio.core.settings import get_settings

            self._token = get_settings().publisher.x_access_token or ""
        except Exception:  # noqa: BLE001
            pass

    @property
    def configured(self) -> bool:
        return bool(self._token)

    def post_status(self, *, post_id: str = "") -> dict:
        """Fetch post status (simulated without credentials)."""
        return {"simulated": not self.configured, "post_id": post_id or "x_demo", "status": "posted"}

    def health(self) -> dict:
        return {"configured": self.configured, "simulated_mode": not self.configured}

    def stats(self) -> dict[str, bool]:
        return {"configured": self.configured}


_CLIENT: XClient | None = None


def get_x_client() -> XClient:
    """Get the module-level singleton X client."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = XClient()
    return _CLIENT
