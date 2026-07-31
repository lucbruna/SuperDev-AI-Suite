"""Factory Context - Shared context for factory operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class FactoryContextItem:
    key: str
    value: Any
    scope: str = "global"
    project_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class FactoryContext:
    def __init__(self):
        self.items: dict[str, FactoryContextItem] = {}
        self.project_contexts: dict[str, dict[str, Any]] = {}

    def set(self, key: str, value: Any, scope: str = "global", project_id: str = "") -> FactoryContextItem:
        item = FactoryContextItem(key=key, value=value, scope=scope, project_id=project_id)
        self.items[key] = item
        if project_id:
            self.project_contexts.setdefault(project_id, {})[key] = value
        return item

    def get(self, key: str, project_id: str = "") -> Any:
        if project_id and project_id in self.project_contexts and key in self.project_contexts[project_id]:
            return self.project_contexts[project_id][key]
        item = self.items.get(key)
        return item.value if item else None

    def delete(self, key: str) -> bool:
        if key in self.items:
            del self.items[key]
            return True
        return False

    def get_project_context(self, project_id: str) -> dict[str, Any]:
        return self.project_contexts.get(project_id, {})

    def list_keys(self, scope: str = None) -> list[str]:
        if scope:
            return [k for k, v in self.items.items() if v.scope == scope]
        return list(self.items.keys())

    def count(self) -> int:
        return len(self.items)
