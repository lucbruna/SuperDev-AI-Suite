"""Security registry for managing security components."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SecurityRegistry:
    """Registry for security components and their configurations."""

    def __init__(self) -> None:
        self._components: Dict[str, Dict[str, Any]] = {}
        self._policies: Dict[str, Dict[str, Any]] = {}

    def register_component(self, name: str, component: Dict[str, Any]) -> None:
        self._components[name] = {**component, "registered": True}

    def get_component(self, name: str) -> Optional[Dict[str, Any]]:
        if name in self._components:
            return dict(self._components[name])
        return None

    def remove_component(self, name: str) -> bool:
        if name in self._components:
            del self._components[name]
            return True
        return False

    def list_components(self) -> List[str]:
        return list(self._components.keys())

    def register_policy(self, policy_id: str, policy: Dict[str, Any]) -> None:
        self._policies[policy_id] = policy

    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        if policy_id in self._policies:
            return dict(self._policies[policy_id])
        return None

    def list_policies(self) -> List[str]:
        return list(self._policies.keys())

    def count(self) -> Dict[str, int]:
        return {"components": len(self._components), "policies": len(self._policies)}
