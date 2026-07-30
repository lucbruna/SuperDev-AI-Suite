from __future__ import annotations

from typing import Any

from .client import BaseClient


class RESTClient(BaseClient):
    """High-level REST client with CRUD convenience methods."""

    def get(self, path: str, *, params: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path: str, *, body: Any = None, **kwargs: Any) -> Any:
        return self.request("POST", path, body=body, **kwargs)

    def put(self, path: str, *, body: Any = None, **kwargs: Any) -> Any:
        return self.request("PUT", path, body=body, **kwargs)

    def patch(self, path: str, *, body: Any = None, **kwargs: Any) -> Any:
        return self.request("PATCH", path, body=body, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self.request("DELETE", path, **kwargs)

    def list(self, path: str, *, page: int = 1, per_page: int = 20, **kwargs: Any) -> Any:
        return self.request("GET", path, params={"page": page, "per_page": per_page, **kwargs})

    def create(self, path: str, data: dict[str, Any], **kwargs: Any) -> Any:
        return self.request("POST", path, body=data, **kwargs)

    def update(self, path: str, data: dict[str, Any], **kwargs: Any) -> Any:
        return self.request("PUT", path, body=data, **kwargs)

    def partial_update(self, path: str, data: dict[str, Any], **kwargs: Any) -> Any:
        return self.request("PATCH", path, body=data, **kwargs)
