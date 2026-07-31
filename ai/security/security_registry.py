"""Security registry for managing security components."""
from __future__ import annotations

from typing import Any


class SecurityRegistry:
    """Registry for security components and their configurations."""

    def __init__(self) -> None:
        self._components: dict[str, dict[str, Any]] = {}
        self._policies: dict[str, dict[str, Any]] = {}

    def register_component(self, name: str, component: dict[str, Any]) -> None:
        self._components[name] = {**component, "registered": True}

    def get_component(self, name: str) -> dict[str, Any] | None:
        if name in self._components:
            return dict(self._components[name])
        return None

    def remove_component(self, name: str) -> bool:
        if name in self._components:
            del self._components[name]
            return True
        return False

    def list_components(self) -> list[str]:
        return list(self._components.keys())

    def register_policy(self, policy_id: str, policy: dict[str, Any]) -> None:
        self._policies[policy_id] = policy

    def get_policy(self, policy_id: str) -> dict[str, Any] | None:
        if policy_id in self._policies:
            return dict(self._policies[policy_id])
        return None

    def list_policies(self) -> list[str]:
        return list(self._policies.keys())

    def count(self) -> dict[str, int]:
        return {"components": len(self._components), "policies": len(self._policies)}
