from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class RepositoriesEngine:
    """Renders the repositories page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.repositories")
        self._context = context or FrontendContext()
        self._repositories: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "repositories",
            "count": len(self._repositories),
            "repositories": self.list(),
        }

    def list(self) -> list[dict[str, Any]]:
        return [
            {"repository_id": repository_id, **repository}
            for repository_id, repository in self._repositories.items()
        ]

    def add(self, name: str, url: str, provider: str = "github") -> str:
        repository_id = f"repo-{len(self._repositories) + 1}"
        self._repositories[repository_id] = {
            "name": name,
            "url": url,
            "provider": provider,
            "status": "active",
            "added_at": time.time(),
        }
        return repository_id

    def remove(self, repository_id: str) -> bool:
        return self._repositories.pop(repository_id, None) is not None

    def sync(self, repository_id: str) -> dict[str, Any]:
        repository = self._repositories.get(repository_id)
        if repository is None:
            raise KeyError(f"unknown repository: {repository_id}")
        repository["last_sync"] = time.time()
        return {"repository_id": repository_id, "synced": True}
