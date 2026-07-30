from __future__ import annotations

from typing import Any

from .github_client import GitHubClient


class PullRequests:
    """GitHub pull request management."""

    def __init__(self, client: GitHubClient):
        self._client = client

    def list(self, state: str = "open", **params: Any) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/pulls", params={"state": state, **params})
        return data.get("data", [])

    def get(self, pr_number: int) -> dict[str, Any]:
        return self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}")

    def create(self, title: str, head: str, base: str, body: str = "", draft: bool = False) -> dict[str, Any]:
        return self._client.post(
            f"/repos/{self._client.owner}/{self._client.repo}/pulls",
            json={"title": title, "head": head, "base": base, "body": body, "draft": draft},
        )

    def update(self, pr_number: int, **kwargs: Any) -> dict[str, Any]:
        return self._client.patch(f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}", json=kwargs)

    def merge(self, pr_number: int, commit_title: str = "", merge_method: str = "merge") -> dict[str, Any]:
        return self._client.put(
            f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/merge",
            json={"commit_title": commit_title, "merge_method": merge_method},
        )

    def list_files(self, pr_number: int) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/files")
        return data.get("data", [])

    def list_reviews(self, pr_number: int) -> list[dict[str, Any]]:
        data = self._client.get(f"/repos/{self._client.owner}/{self._client.repo}/pulls/{pr_number}/reviews")
        return data.get("data", [])
