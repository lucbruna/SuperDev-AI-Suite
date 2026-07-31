"""Organization hierarchy."""
from __future__ import annotations

from typing import Any


class OrganizationHierarchy:
    def __init__(self) -> None:
        self._tree: dict[str, dict[str, Any]] = {}
    def set_parent(self, org_id: str, parent_id: str) -> None:
        self._tree.setdefault(org_id, {})["parent"] = parent_id
        self._tree.setdefault(parent_id, {}).setdefault("children", []).append(org_id)
    def get_parent(self, org_id: str) -> str | None:
        return self._tree.get(org_id, {}).get("parent")
    def get_children(self, org_id: str) -> list[str]:
        return list(self._tree.get(org_id, {}).get("children", []))
    def get_all_descendants(self, org_id: str) -> list[str]:
        descendants = []
        for child in self.get_children(org_id):
            descendants.append(child)
            descendants.extend(self.get_all_descendants(child))
        return descendants
    def is_child_of(self, org_id: str, potential_parent: str) -> bool:
        parent = self.get_parent(org_id)
        while parent:
            if parent == potential_parent:
                return True
            parent = self.get_parent(parent)
        return False
    def get_root(self, org_id: str) -> str:
        current = org_id
        while self.get_parent(current):
            current = self.get_parent(current)
        return current
    def list_all(self) -> dict[str, dict[str, Any]]:
        return dict(self._tree)
