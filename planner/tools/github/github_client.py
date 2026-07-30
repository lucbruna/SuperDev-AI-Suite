from __future__ import annotations

from typing import Any


class GitHubClient:
    """Base HTTP client for GitHub API interactions."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str = "", owner: str = "", repo: str = ""):
        self.token = token
        self.owner = owner
        self.repo = repo
        self._headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    def set_owner_repo(self, owner: str, repo: str) -> None:
        self.owner = owner
        self.repo = repo

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        return {"status": 200, "data": {}, "method": method, "path": path}

    def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("PATCH", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self._request("DELETE", path, **kwargs)

    def rate_limit(self) -> dict[str, Any]:
        return {"remaining": 5000, "limit": 5000, "reset": 0}
