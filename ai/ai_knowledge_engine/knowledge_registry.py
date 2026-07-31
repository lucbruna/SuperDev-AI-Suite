"""Knowledge Registry — Registry for knowledge components."""

from typing import Any


class KnowledgeRegistry:
    def __init__(self):
        self._components: dict[str, dict[str, Any]] = {}
        self._categories: dict[str, list[str]] = {}

    def register(
        self, name: str, component: Any, category: str = "default", metadata: dict[str, Any] | None = None
    ) -> None:
        self._components[name] = {"component": component, "category": category, "metadata": metadata or {}}
        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)

    def get(self, name: str) -> Any | None:
        entry = self._components.get(name)
        return entry["component"] if entry else None

    def get_by_category(self, category: str) -> dict[str, Any]:
        names = self._categories.get(category, [])
        return {name: self._components[name]["component"] for name in names if name in self._components}

    def unregister(self, name: str) -> bool:
        entry = self._components.pop(name, None)
        if entry:
            cat = entry["category"]
            if cat in self._categories and name in self._categories[cat]:
                self._categories[cat].remove(name)
            return True
        return False

    def list_components(self) -> list[str]:
        return list(self._components.keys())

    def list_categories(self) -> list[str]:
        return list(self._categories.keys())

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_components": len(self._components),
            "categories": len(self._categories),
            "components_by_category": {cat: len(names) for cat, names in self._categories.items()},
        }
