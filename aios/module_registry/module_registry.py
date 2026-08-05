"""ModuleRegistry: storage and lookup for registered modules."""
from __future__ import annotations

from typing import Any, Optional

from aios.module_registry.module import Module


class ModuleRegistry:
    """In-memory module store with deterministic sequential ids."""

    def __init__(self) -> None:
        self._modules: dict[str, Module] = {}
        self._by_name: dict[str, str] = {}
        self._seq = 0

    def register(
        self,
        name: str,
        version: str = "1.0.0",
        entrypoint: Any = None,
        capabilities: list[str] | None = None,
        dependencies: list[str] | None = None,
        module_id: str | None = None,
        **metadata: Any,
    ) -> Module:
        if name in self._by_name:
            raise KeyError(f"module name {name!r} already registered")
        self._seq += 1
        module = Module(
            module_id=module_id or f"mod-{self._seq:04d}",
            name=name,
            version=str(version),
            entrypoint=entrypoint,
            capabilities=list(capabilities or []),
            dependencies=list(dependencies or []),
            metadata=dict(metadata),
        )
        self._modules[module.module_id] = module
        self._by_name[name] = module.module_id
        return module

    def unregister(self, module_id: str) -> bool:
        module = self._modules.pop(module_id, None)
        if module is None:
            return False
        if self._by_name.get(module.name) == module_id:
            del self._by_name[module.name]
        return True

    def get(self, module_id: str) -> Optional[Module]:
        return self._modules.get(module_id)

    def get_by_name(self, name: str) -> Optional[Module]:
        module_id = self._by_name.get(name)
        return self._modules.get(module_id) if module_id is not None else None

    def modules(self) -> list[Module]:
        return [self._modules[module_id] for module_id in sorted(self._modules)]

    def by_capability(self, capability: str) -> list[Module]:
        return [module for module in self.modules() if capability in module.capabilities]

    def by_status(self, status: str) -> list[Module]:
        return [module for module in self.modules() if module.status == status]

    def stats(self) -> dict[str, Any]:
        return {
            "total": len(self._modules),
            "names": sorted(self._by_name),
            "capabilities": sorted({cap for module in self._modules.values() for cap in module.capabilities}),
        }
