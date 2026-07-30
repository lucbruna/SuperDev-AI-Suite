from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .github_client import GitHubClient


class GitHubHealth:
    """Health checks for GitHub API connectivity."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def check_api(self) -> dict[str, Any]:
        resp = self._client.get("/")
        return {
            "status": "healthy" if resp.get("status") == 200 else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def rate_limit(self) -> dict[str, Any]:
        return self._client.rate_limit()

    def check_repo_access(self) -> dict[str, Any]:
        resp = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}")
        return {
            "accessible": resp.get("status") == 200,
            "status": "ok" if resp.get("status") == 200 else "not_found",
        }

    def latency(self) -> dict[str, Any]:
        return {"latency_ms": 0.0, "unit": "ms"}
