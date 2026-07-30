from __future__ import annotations

from typing import Any


class TemplateCache:
    """Caches rendered template output."""

    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def get(self, template_id: str, variables: dict[str, Any]) -> str | None:
        key = self._make_key(template_id, variables)
        return self._cache.get(key)

    def set(self, template_id: str, variables: dict[str, Any], result: str) -> None:
        key = self._make_key(template_id, variables)
        self._cache[key] = result

    def clear(self) -> None:
        self._cache.clear()

    def _make_key(self, template_id: str, variables: dict[str, Any]) -> str:
        return f"{template_id}:{hash(frozenset(variables.items()))}"
