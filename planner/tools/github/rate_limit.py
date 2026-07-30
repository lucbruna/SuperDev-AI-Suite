from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class RateLimit:
    """GitHub API rate limit monitoring."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def get(self) -> dict[str, Any]:
        return self._client.rate_limit()

    def remaining(self) -> int:
        data = self.get()
        return data.get("remaining", 0)

    def limit(self) -> int:
        data = self.get()
        return data.get("limit", 5000)

    def reset_time(self) -> int:
        data = self.get()
        return data.get("reset", 0)

    def is_limited(self) -> bool:
        return self.remaining() == 0

    def wait_time(self) -> float:
        import time
        reset = self.reset_time()
        now = time.time()
        return max(0.0, reset - now)

    def check_endpoint(self, endpoint: str = "") -> dict[str, Any]:
        return {"endpoint": endpoint, "remaining": self.remaining(), "limited": self.is_limited()}
