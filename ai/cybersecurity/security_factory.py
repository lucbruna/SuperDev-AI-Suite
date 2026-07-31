"""
Security Factory
"""

from typing import Any


class SecurityFactory:
    def __init__(self):
        self._creators: dict[str, type] = {}
        self._instances: dict[str, Any] = {}

    def register(self, name: str, creator_class: type) -> None:
        self._creators[name] = creator_class

    def create(self, name: str, **kwargs) -> Any:
        if name not in self._creators:
            raise ValueError(f"Unknown component: {name}")
        return self._creators[name](**kwargs)

    def create_singleton(self, name: str, **kwargs) -> Any:
        if name not in self._instances:
            self._instances[name] = self.create(name, **kwargs)
        return self._instances[name]

    def get_singleton(self, name: str) -> Any | None:
        return self._instances.get(name)

    def list_registered(self) -> list:
        return list(self._creators.keys())

    def list_singletons(self) -> list:
        return list(self._instances.keys())
