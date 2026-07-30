from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Labels:
    """GitHub label management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/labels")
        return data.get("data", [])

    def get(self, name: str) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/labels/{name}")

    def create(self, name: str, color: str = "000000", description: str = "") -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/labels",
            json={"name": name, "color": color, "description": description},
        )

    def update(self, current_name: str, **kwargs: Any) -> dict[str, Any]:
        return self._client.patch(
            f"/repos/{self._client.owner}/{self._client.repo}/labels/{current_name}",
            json=kwargs,
        )

    def delete(self, name: str) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/labels/{name}")
