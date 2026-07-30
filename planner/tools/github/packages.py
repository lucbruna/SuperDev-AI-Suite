from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class Packages:
    """GitHub Packages management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self, package_type: str = "container", visibility: str = "private") -> list[dict[str, Any]]:
        data = self._client.get(
            f"/users/{self._client.owner}/packages",
            params={"package_type": package_type, "visibility": visibility},
        )
        return data.get("data", [])

    def get(self, package_type: str, package_name: str) -> dict[str, Any]:
        return self._client.get(
            f"/users/{self._client.owner}/packages/{package_type}/{package_name}"
        )

    def list_versions(self, package_type: str, package_name: str) -> list[dict[str, Any]]:
        data = self._client.get(
            f"/users/{self._client.owner}/packages/{package_type}/{package_name}/versions"
        )
        return data.get("data", [])

    def get_version(self, package_type: str, package_name: str, version_id: int) -> dict[str, Any]:
        return self._client.get(
            f"/users/{self._client.owner}/packages/{package_type}/{package_name}/versions/{version_id}"
        )

    def delete(self, package_type: str, package_name: str) -> dict[str, Any]:
        return self._client.delete(
            f"/users/{self._client.owner}/packages/{package_type}/{package_name}"
        )

    def restore(self, package_type: str, package_name: str, version_id: int) -> dict[str, Any]:
        return self._client.post(
            f"/users/{self._client.owner}/packages/{package_type}/{package_name}/versions/{version_id}/restore"
        )
