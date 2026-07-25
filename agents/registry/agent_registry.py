from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
from typing import Any, Optional, type_checking

from ..base.base_agent import BaseAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, type[BaseAgent]] = {}

    def register(self, name: str, agent_class: type[BaseAgent]) -> None:
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{agent_class.__name__} must be a subclass of BaseAgent")
        self._agents[name] = agent_class

    def get(self, name: str) -> Optional[type[BaseAgent]]:
        return self._agents.get(name)

    def list(self) -> dict[str, type[BaseAgent]]:
        return dict(self._agents)

    def unregister(self, name: str) -> None:
        self._agents.pop(name, None)

    def discover(self, package_path: str) -> None:
        package_dir = os.path.dirname(os.path.abspath(package_path))
        for importer, modname, ispkg in pkgutil.iter_modules([package_dir]):
            if modname.endswith("_agent"):
                try:
                    module = importlib.import_module(modname)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                            registry_name = getattr(obj, "_registry_name", modname)
                            self.register(registry_name, obj)
                except Exception:
                    pass
