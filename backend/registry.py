from __future__ import annotations

from typing import Any


class ServiceRegistry:
    _instance: ServiceRegistry | None = None

    def __new__(cls) -> ServiceRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._services: dict[str, Any] = {}
            cls._instance._categories: dict[str, dict[str, Any]] = {
                "services": {},
                "providers": {},
                "agents": {},
                "plugins": {},
                "tools": {},
            }
        return cls._instance

    def register(self, name: str, service: Any, category: str | None = None) -> None:
        self._services[name] = service
        if category and category in self._categories:
            self._categories[category][name] = service

    def get(self, name: str, default: Any = None) -> Any:
        return self._services.get(name, default)

    def get_all(self, category: str | None = None) -> dict[str, Any]:
        if category:
            return dict(self._categories.get(category, {}))
        return dict(self._services)

    def remove(self, name: str) -> None:
        self._services.pop(name, None)
        for category in self._categories.values():
            category.pop(name, None)

    def clear(self) -> None:
        self._services.clear()
        for category in self._categories.values():
            category.clear()

    def list_categories(self) -> list[str]:
        return list(self._categories.keys())

    def list_services(self, category: str | None = None) -> list[str]:
        if category:
            return list(self._categories.get(category, {}).keys())
        return list(self._services.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._services


service_registry = ServiceRegistry()
