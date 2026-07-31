"""BI Context — Shared context for BI operations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BIContextItem:
    key: str
    value: Any
    scope: str = "global"
    project_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class BIContext:
    def __init__(self):
        self.items: dict[str, BIContextItem] = {}
        self.project_contexts: dict[str, dict[str, Any]] = {}

    def set(self, key: str, value: Any, scope: str = "global", project_id: str = "") -> BIContextItem:
        item = BIContextItem(key=key, value=value, scope=scope, project_id=project_id)
        self.items[key] = item
        if project_id:
            self.project_contexts.setdefault(project_id, {})[key] = value
        return item

    def get(self, key: str, project_id: str = "") -> Any:
        if project_id and project_id in self.project_contexts:
            return self.project_contexts[project_id].get(key)
        item = self.items.get(key)
        return item.value if item else None

    def delete(self, key: str) -> bool:
        if key in self.items:
            del self.items[key]
            return True
        return False

    def get_all(self) -> dict[str, Any]:
        return {k: v.value for k, v in self.items.items()}

    def count(self) -> int:
        return len(self.items)
