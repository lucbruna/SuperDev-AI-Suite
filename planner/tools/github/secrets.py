from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Secrets:
    """GitHub repository secrets management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/actions/secrets")
        return data.get("data", [])

    def get(self, name: str) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/actions/secrets/{name}")

    def create(self, name: str, value: str) -> dict[str, Any]:
        return self._client.put(
            f"/repos/{self._client.owner}/{self._client.repo}/actions/secrets/{name}",
            json={"encrypted_value": value, "key_id": "mock-key"},
        )

    def update(self, name: str, value: str) -> dict[str, Any]:
        return self.create(name, value)

    def delete(self, name: str) -> dict[str, Any]:
        return self._client.delete(f"/repos/{self._client.owner}/{self._client.repo}/actions/secrets/{name}")
