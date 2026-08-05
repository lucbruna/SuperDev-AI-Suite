"""AIOS extensions subsystem: extension lifecycle, hooks, and plugin loading."""
from aios.extensions.extension import (
    HOOK_POINTS,
    Extension,
    ExtensionContext,
    HookFunc,
)
from aios.extensions.extension_manager import ExtensionManager, make_extension_manager
from aios.extensions.hook_registry import FireResult, HookEntry, HookRegistry
from aios.extensions.plugin_loader import ExtensionFactory, PluginLoader

__all__ = [
    "Extension",
    "ExtensionContext",
    "ExtensionFactory",
    "ExtensionManager",
    "FireResult",
    "HOOK_POINTS",
    "HookEntry",
    "HookFunc",
    "HookRegistry",
    "PluginLoader",
    "make_extension_manager",
]
