from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Actions:
    """GitHub Actions artifact and secret management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list_artifacts(self, run_id: int | None = None) -> list[dict[str, Any]]:
        path = f"/repos/{self._client.owner}/{self._client.repo}/actions/artifacts"
        if run_id is not None:
            path = f"/repos/{self._client.owner}/{self._client.repo}/actions/runs/{run_id}/artifacts"
        data = self._client.get(path)
        return data.get("data", [])

    def download_artifact(self, artifact_id: int) -> bytes:
        return b""

    def upload_artifact(self, name: str, data: bytes) -> dict[str, Any]:
        return {"id": 0, "name": name}

    def list_secrets(self) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/actions/secrets")
        return data.get("data", [])

    def create_secret(self, name: str, value: str) -> dict[str, Any]:
        return self._client.put(
            f"/repos/{self._client.owner}/{self._client.repo}/actions/secrets/{name}",
            json={"encrypted_value": value, "key_id": "mock"},
        )
