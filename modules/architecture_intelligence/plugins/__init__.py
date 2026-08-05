"""Plugin registry for intelligence extensions."""
from __future__ import annotations

from modules.architecture_intelligence.plugins.registry import (
    PluginRegistry,
    get_plugin_registry,
    register_plugin,
)

__all__ = ["PluginRegistry", "get_plugin_registry", "register_plugin"]
