from __future__ import annotations

import logging
from typing import Any

from ..design_system import DesignEngine


class ComponentsEngine:
    """Coordinates the reusable component library."""

    def __init__(self, design: DesignEngine | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.components")
        self.design = design or DesignEngine()
        self._components: dict[str, Any] = {}

    def register(self, name: str, component: Any) -> None:
        self._components[name] = component

    def get(self, name: str) -> Any:
        if name not in self._components:
            raise KeyError(f"unknown component: {name}")
        return self._components[name]

    def render(self, name: str, **props: Any) -> dict[str, Any]:
        component = self.get(name)
        if hasattr(component, "render"):
            return component.render(self.design, **props)
        return {"type": name, "props": props}

    def list(self) -> list[str]:
        return sorted(self._components)

    def token(self, name: str) -> str:
        return self.design.colors.color(name)


__all__ = ["ComponentsEngine"]
