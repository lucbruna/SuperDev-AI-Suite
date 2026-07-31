from __future__ import annotations

import importlib
import pkgutil
from typing import Any

from ..base.base_tool import BaseTool
from .tool_interfaces import ITool


class ToolLoader:
    """Dynamically loads tool modules from packages."""

    def __init__(self) -> None:
        self._loaded: dict[str, ITool] = {}

    def load_module(self, module_path: str) -> list[ITool]:
        module = importlib.import_module(module_path)
        tools: list[ITool] = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseTool) and attr is not BaseTool:
                instance = attr()
                self._loaded[instance.name()] = instance
                tools.append(instance)
        return tools

    def load_directory(self, package_path: str) -> list[ITool]:
        tools: list[ITool] = []
        try:
            package = importlib.import_module(package_path)
            for _importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
                if not ispkg:
                    full_path = f"{package_path}.{modname}"
                    tools.extend(self.load_module(full_path))
        except (ImportError, AttributeError):
            pass
        return tools

    def get_loaded(self, name: str) -> ITool | None:
        return self._loaded.get(name)

    def list_loaded(self) -> list[str]:
        return list(self._loaded.keys())

    @property
    def loaded_count(self) -> int:
        return len(self._loaded)

    def to_dict(self) -> dict[str, Any]:
        return {
            "loaded": list(self._loaded.keys()),
            "loaded_count": self.loaded_count,
        }
