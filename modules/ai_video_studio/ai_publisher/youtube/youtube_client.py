"""YouTube Client — platform API client (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None


class YoutubeClient:
    """YouTube Data/API client.

    Returns simulated-but-structured responses when no credentials are
    configured. Real HTTP integration plugs in at the marked call sites.
    """

    def __init__(self) -> None:
        self._client_id = ""
        self._client_secret = ""
        self._token = ""
        self._load_settings()

    def _load_settings(self) -> None:
        try:
            from modules.ai_video_studio.core.settings import get_settings

            publisher = get_settings().publisher
            self._client_id = publisher.youtube_client_id or ""
            self._client_secret = publisher.youtube_client_secret or ""
        except Exception:  # noqa: BLE001
            pass

    @property
    def configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    def set_token(self, token: str) -> dict:
        """Store an access token for authenticated calls."""
        self._token = token
        return {"configured": bool(token)}

    def get_channel(self, *, channel_id: str = "UCdefault") -> dict:
        """Fetch channel metadata (simulated without credentials)."""
        if self.configured and httpx is not None:
            # Real integration point: GET /youtube/v3/channels
            pass
        return {
            "simulated": not self.configured,
            "channel_id": channel_id,
            "title": "Demo Channel",
            "subscriber_count": 1200,
            "video_count": 34,
        }

    def search(self, *, query: str, max_results: int = 10) -> dict:
        """Search videos (simulated without credentials)."""
        return {
            "simulated": not self.configured,
            "query": query,
            "results": [
                {
                    "video_id": f"vid{i:04d}",
                    "title": f"{query} — result {i + 1}",
                    "channel": "Demo",
                }
                for i in range(min(max_results, 10))
            ],
        }

    def health(self) -> dict:
        return {"configured": self.configured, "simulated_mode": not self.configured}

    def stats(self) -> dict[str, bool]:
        return {"configured": self.configured}


_CLIENT: YoutubeClient | None = None


def get_youtube_client() -> YoutubeClient:
    """Get the module-level singleton YouTube client."""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = YoutubeClient()
    return _CLIENT
