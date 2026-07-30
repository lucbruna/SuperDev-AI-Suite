from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Commits:
    """GitHub commit operations."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self, branch: str = "main", **params: Any) -> list[dict[str, Any]]:
        data = self._client.get(
            f"/repos/{self._client.owner}/{self._client.repo}/commits",
            params={"sha": branch, **params},
        )
        return data.get("data", [])

    def get(self, sha: str) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/commits/{sha}")

    def compare(self, base: str, head: str) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/compare/{base}...{head}")

    def list_files(self, sha: str) -> list[dict[str, Any]]:
        data = self.get(sha)
        return data.get("data", {}).get("files", [])

    def list_statuses(self, ref: str) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/commits/{ref}/statuses")
        return data.get("data", [])
