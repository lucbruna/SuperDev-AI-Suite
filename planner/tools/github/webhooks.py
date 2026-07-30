from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Webhooks:
    """GitHub webhook management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/hooks")
        return data.get("data", [])

    def create(self, url: str, events: list[str], secret: str = "", active: bool = True) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/hooks",
            json={"name": "web", "config": {"url": url, "content_type": "json", "secret": secret}, "events": events, "active": active},
        )

    def update(self, hook_id: int, **kwargs: Any) -> dict[str, Any]:
        return self._client.patch(f"/repos/{self._client.owner}/{self._client.repo}/hooks/{hook_id}", json=kwargs)

    def delete(self, hook_id: int) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/hooks/{hook_id}")

    def list_deliveries(self, hook_id: int) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/hooks/{hook_id}/deliveries")
        return data.get("data", [])

    def redeliver(self, hook_id: int, delivery_id: int) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/hooks/{hook_id}/deliveries/{delivery_id}/attempts"
        )
