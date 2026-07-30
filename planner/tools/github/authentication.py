from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Authentication:
    """GitHub authentication management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def get_authenticated_user(self) -> dict[str, Any]:
        return self._client.get("/user")

    def list_ssh_keys(self) -> list[dict[str, Any]]:
        data = self._client.get("/user/keys")
        return data.get("data", [])

    def add_ssh_key(self, title: str, key: str) -> dict[str, Any]:
        return self._client.post("/user/keys", json={"title": title, "key": key})

    def delete_ssh_key(self, key_id: int) -> dict[str, Any]:
        return self._client.delete(f"/user/keys/{key_id}")

    def list_gpg_keys(self) -> list[dict[str, Any]]:
        data = self._client.get("/user/gpg_keys")
        return data.get("data", [])

    def add_gpg_key(self, armored_public_key: str) -> dict[str, Any]:
        return self._client.post("/user/gpg_keys", json={"armored_public_key": armored_public_key})

    def delete_gpg_key(self, key_id: int) -> dict[str, Any]:
        return self._client.delete(f"/user/gpg_keys/{key_id}")

    def get_org_membership(self, org: str) -> dict[str, Any]:
        return self._client.get(f"/user/memberships/orgs/{org}")
