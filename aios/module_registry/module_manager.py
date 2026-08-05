"""ModuleManager: facade for the module system (register, resolve, install, lifecycle)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from aios.module_registry.module import Module
from aios.module_registry.module_dependency_manager import ModuleDependencyManager
from aios.module_registry.module_lifecycle import ModuleLifecycle
from aios.module_registry.module_loader import ModuleLoader
from aios.module_registry.module_registry import ModuleRegistry
from aios.module_registry.module_resolver import ModuleResolution, ModuleResolver


@dataclass
class InstallResult:
    module_id: str
    ok: bool
    status: str
    resolution: ModuleResolution = field(default_factory=ModuleResolution)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "ok": self.ok,
            "status": self.status,
            "resolution": self.resolution.to_dict(),
        }


class ModuleManager:
    def __init__(
        self,
        registry: ModuleRegistry | None = None,
        dependencies: ModuleDependencyManager | None = None,
        resolver: ModuleResolver | None = None,
        lifecycle: ModuleLifecycle | None = None,
        loader: ModuleLoader | None = None,
    ) -> None:
        self.registry = registry if registry is not None else ModuleRegistry()
        self.dependencies = dependencies if dependencies is not None else ModuleDependencyManager()
        self.resolver = resolver if resolver is not None else ModuleResolver(self.dependencies)
        self.lifecycle = lifecycle if lifecycle is not None else ModuleLifecycle()
        self.loader = loader if loader is not None else ModuleLoader(self.lifecycle)

    def register(
        self,
        name: str,
        version: str = "1.0.0",
        entrypoint: Callable[[], Any] | None = None,
        capabilities: list[str] | None = None,
        dependencies: list[str] | None = None,
        module_id: str | None = None,
        **metadata: Any,
    ) -> Module:
        module = self.registry.register(
            name=name,
            version=version,
            entrypoint=entrypoint,
            capabilities=capabilities,
            dependencies=dependencies,
            module_id=module_id,
            **metadata,
        )
        self.lifecycle.set_state(module.module_id, "registered")
        return module

    def resolve(self) -> ModuleResolution:
        return self.resolver.resolve(self.registry.modules())

    def install(self, name: str) -> InstallResult:
        module = self.registry.get_by_name(name)
        if module is None:
            raise KeyError(f"module {name!r} not registered")
        resolution = self.resolve()
        if resolution.ok:
            ok = True
            for resolved_name in resolution.resolved:
                target = self.registry.get_by_name(resolved_name)
                if target is not None and not self.loader.load(target):
                    ok = False
                    break
            status = "active" if ok else "failed"
        else:
            ok = False
            status = "registered"
        return InstallResult(module_id=module.module_id, ok=ok, status=status, resolution=resolution)

    def activate(self, module_id: str) -> bool:
        module = self._require(module_id)
        return self.lifecycle.set_state(module.module_id, "active") and module.status == "active"

    def deactivate(self, module_id: str) -> bool:
        module = self._require(module_id)
        ok = self.lifecycle.set_state(module.module_id, "inactive")
        if ok:
            module.status = "inactive"
        return ok

    def uninstall(self, module_id: str) -> bool:
        module = self._require(module_id)
        if not self.lifecycle.set_state(module.module_id, "unloaded"):
            return False
        self.registry.unregister(module_id)
        self.dependencies.remove_module(module.name)
        return True

    def status(self, module_id: str) -> Optional[str]:
        return self.lifecycle.state(module_id)

    def _require(self, module_id: str) -> Module:
        module = self.registry.get(module_id)
        if module is None:
            raise KeyError(f"unknown module {module_id!r}")
        return module

    def snapshot(self) -> dict[str, Any]:
        return {
            "modules": len(self.registry.modules()),
            "active": sum(
                1 for module in self.registry.modules()
                if self.status(module.module_id) == "active"
            ),
            "events": len(self.lifecycle.events()),
            "registry": self.registry.stats(),
        }
