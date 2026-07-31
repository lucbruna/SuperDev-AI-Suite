from __future__ import annotations

from typing import Any


class RepositoryGenerator:
    """Generates and manages repository/data access layer classes."""

    def __init__(self) -> None:
        self._repositories: dict[str, dict[str, Any]] = {}

    def add_repository(
        self,
        name: str,
        entity: str,
        methods: list[str] | None = None,
    ) -> str:
        self._repositories[name] = {
            "name": name,
            "entity": entity,
            "methods": methods or ["find_all", "find_by_id", "save", "delete"],
        }
        return name

    def get_repository(self, name: str) -> dict[str, Any] | None:
        return self._repositories.get(name)

    def list_repositories(self) -> list[dict[str, Any]]:
        return list(self._repositories.values())

    @property
    def repository_count(self) -> int:
        return len(self._repositories)

    def generate_repository_code(self, name: str) -> str:
        repo = self._repositories.get(name)
        if repo is None:
            return f"# Repository '{name}' not found"
        methods_code = "\n".join(f"    async def {m}(self) -> Any:\n        ..." for m in repo["methods"])
        return (
            f"from __future__ import annotations\n\nfrom typing import Any\n\n\n"
            f"class {name}:\n\n    def __init__(self) -> None:\n"
            f"        self._entity = '{repo['entity']}'\n\n{methods_code}\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "repositories": list(self._repositories.values()),
            "repository_count": self.repository_count,
        }
