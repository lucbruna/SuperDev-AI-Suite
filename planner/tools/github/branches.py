from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Branches:
    """GitHub branch management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/branches")
        return data.get("data", [])

    def get(self, branch: str) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/branches/{branch}")

    def create(self, name: str, sha: str) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/git/refs",
            json={"ref": f"refs/heads/{name}", "sha": sha},
        )

    def delete(self, branch: str) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/git/refs/heads/{branch}")

    def merge(self, base: str, head: str, commit_message: str = "") -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/merges",
            json={"base": base, "head": head, "commit_message": commit_message},
        )

    def protect(self, branch: str) -> dict[str, Any]:
        return self._client.put(
            f"/repos/{self._client.owner}/{self._client.repo}/branches/{branch}/protection",
            json={"required_status_checks": None, "enforce_admins": True},
        )

    def unprotect(self, branch: str) -> dict[str, Any]:
        return self._client.delete(
            f"/repos/{self._client.owner}/{self._client.repo}/branches/{branch}/protection"
        )
