from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Repository:
    """GitHub repository operations."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def get(self) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}")

    def create(self, name: str, private: bool = False, description: str = "") -> dict[str, Any]:
        return self._client.post("/user/repos", json={"name": name, "private": private, "description": description})

    def fork(self, owner: str, repo: str) -> dict[str, Any]:
        return self._client.post(f"/repos/{owner}/{repo}/forks")

    def list_branches(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/branches")
        return data.get("data", [])

    def list_contributors(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/contributors")
        return data.get("data", [])
