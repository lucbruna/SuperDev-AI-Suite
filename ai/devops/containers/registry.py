"""Container registry."""
from __future__ import annotations

import time
from typing import Any


class ContainerRegistry:
    def __init__(self) -> None:
        self._repositories: dict[str, dict[str, Any]] = {}
    def create_repository(self, name: str, description: str = "") -> dict[str, Any]:
        repo = {"name": name, "description": description, "tags": [], "created_at": time.time()}
        self._repositories[name] = repo
        return repo
    def push(self, repository: str, tag: str, image_id: str) -> dict[str, Any]:
        if repository not in self._repositories:
            self.create_repository(repository)
        self._repositories[repository]["tags"].append({"tag": tag, "image_id": image_id, "pushed_at": time.time()})
        return {"repository": repository, "tag": tag, "pushed": True}
    def pull(self, repository: str, tag: str = "latest") -> dict[str, Any]:
        repo = self._repositories.get(repository, {})
        for t in repo.get("tags", []):
            if t["tag"] == tag:
                return {"repository": repository, "tag": tag, "image_id": t["image_id"]}
        return {"error": "tag_not_found"}
    def list_repositories(self) -> list[dict[str, Any]]:
        return list(self._repositories.values())
    def get_tags(self, repository: str) -> list[str]:
        repo = self._repositories.get(repository, {})
        return [t["tag"] for t in repo.get("tags", [])]
    def delete_repository(self, name: str) -> bool:
        if name in self._repositories:
            del self._repositories[name]
            return True
        return False
    def count(self) -> int:
        return len(self._repositories)
