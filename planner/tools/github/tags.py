from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Tags:
    """GitHub tag management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/tags")
        return data.get("data", [])

    def get(self, tag: str) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/git/ref/tags/{tag}")

    def create(self, name: str, sha: str, type: str = "commit") -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/git/refs",
            json={"ref": f"refs/tags/{name}", "sha": sha},
        )

    def create_annotated(self, name: str, sha: str, message: str, tagger: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/git/tags",
            json={"tag": name, "sha": sha, "message": message, "tagger": tagger or {}},
        )

    def delete(self, tag: str) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/git/refs/tags/{tag}")
