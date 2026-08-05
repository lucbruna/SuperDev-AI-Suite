"""AIOS module_registry subsystem: module lifecycle, resolution and installation."""
from aios.module_registry.module import Module
from aios.module_registry.module_dependency_manager import ModuleDependencyManager
from aios.module_registry.module_lifecycle import MODULE_STATES, MODULE_TRANSITIONS, ModuleLifecycle
from aios.module_registry.module_loader import ModuleLoader
from aios.module_registry.module_manager import InstallResult, ModuleManager
from aios.module_registry.module_registry import ModuleRegistry
from aios.module_registry.module_resolver import ModuleResolution, ModuleResolver
from aios.module_registry.module_version import ModuleVersion

__all__ = [
    "Module",
    "ModuleDependencyManager",
    "MODULE_STATES",
    "MODULE_TRANSITIONS",
    "ModuleLifecycle",
    "ModuleLoader",
    "InstallResult",
    "ModuleManager",
    "ModuleRegistry",
    "ModuleResolution",
    "ModuleResolver",
    "ModuleVersion",
]
