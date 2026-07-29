from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class KnowledgeRegistry:
    def __init__(self):
        self._components: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, component: Any,
                 component_type: str = "",
                 subsystem: str = "core",
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        self._components[name] = {
            "name": name,
            "component": component,
            "type": component_type,
            "subsystem": subsystem,
            "metadata": metadata or {},
        }

    def unregister(self, name: str) -> bool:
        if name in self._components:
            del self._components[name]
            return True
        return False

    def get(self, name: str):
        entry = self._components.get(name)
        return entry.get("component") if entry else None

    def get_info(self, name: str) -> Optional[Dict[str, Any]]:
        entry = self._components.get(name)
        return dict(entry) if entry else None

    def list_all(self) -> List[Dict[str, Any]]:
        return [{k: v for k, v in entry.items() if k != "component"}
                for entry in self._components.values()]

    def get_by_type(self, component_type: str) -> List[Dict[str, Any]]:
        return [dict(entry) for entry in self._components.values()
                if entry["type"] == component_type]

    def get_available_subsystems(self) -> List[str]:
        subsystems = set()
        for entry in self._components.values():
            subsystems.add(entry["subsystem"])
        return sorted(subsystems)

    def get_subsystem_components(self, subsystem: str) -> List[Dict[str, Any]]:
        return [dict(entry) for entry in self._components.values()
                if entry["subsystem"] == subsystem]

    def has_component(self, name: str) -> bool:
        return name in self._components

    def count(self) -> int:
        return len(self._components)

    def clear(self) -> None:
        self._components.clear()