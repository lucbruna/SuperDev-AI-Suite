from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Releases:
    """GitHub release management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/releases")
        return data.get("data", [])

    def get(self, release_id: int) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/releases/{release_id}")

    def create(self, tag: str, name: str = "", body: str = "", draft: bool = False, prerelease: bool = False) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/releases",
            json={"tag_name": tag, "name": name, "body": body, "draft": draft, "prerelease": prerelease},
        )

    def update(self, release_id: int, **kwargs: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/repos/{self._client.owner}/{self._client.repo}/releases/{release_id}",
            json=kwargs,
        )

    def delete(self, release_id: int) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/releases/{release_id}")

    def upload_asset(self, release_id: int, name: str, data: bytes) -> dict[str, Any]:
        return {"id": 0, "name": name, "size": len(data)}

    def list_assets(self, release_id: int) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/releases/{release_id}/assets")
        return data.get("data", [])
