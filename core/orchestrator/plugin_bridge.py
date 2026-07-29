"""Plugin Bridge — integration between Orchestrator and Plugin Manager.

Wraps the existing core/plugin_manager/ module into the orchestrator's
service architecture, handling plugin lifecycle (load, enable, disable,
uninstall) and event propagation.
"""

from __future__ import annotations

import os
from typing import Any

from .exceptions import OrchestratorError
from .types import now_iso


class PluginBridge:
    """Bridge between the Orchestrator and the Plugin Manager.

    Handles the full plugin lifecycle: discovery, installation,
    activation, deactivation, and removal. Integrates with the
    existing core/plugin_manager/ module through lazy imports.
    """

    def __init__(self, event_bus: Any = None) -> None:
        self._event_bus = event_bus
        self._plugin_manager: Any = None
        self._initialized = False
        self._loaded_plugins: dict[str, dict[str, Any]] = {}

    async def initialize(self) -> bool:
        """Initialize the plugin bridge."""
        try:
            from core.plugin_manager.core.plugin_manager import PluginManager
            from core.plugin_manager.core.plugin_configuration import PluginConfiguration

            config = PluginConfiguration()
            self._plugin_manager = PluginManager(config)
            self._initialized = True
            return True
        except ImportError as e:
            raise OrchestratorError(f"Failed to initialize PluginBridge: {e}")

    async def load_plugins(self) -> list[dict[str, Any]]:
        """Discover and load all available plugins."""
        if not self._plugin_manager:
            raise OrchestratorError("PluginBridge not initialized")

        try:
            from core.plugin_manager.loader.plugin_loader import PluginLoader
            from core.plugin_manager.registry.plugin_registry import PluginRegistry

            loader = PluginLoader()
            registry = PluginRegistry()

            plugin_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "plugins",
            )
            if os.path.exists(plugin_dir):
                plugins = loader.discover(plugin_dir)
                for plugin in plugins:
                    registry.register(plugin)
                    self._loaded_plugins[plugin.name] = {
                        "name": plugin.name,
                        "version": getattr(plugin, "version", "1.0.0"),
                        "status": "loaded",
                        "loaded_at": now_iso(),
                    }
                    if self._event_bus:
                        await self._event_bus.publish(
                            "plugin.loaded",
                            {"name": plugin.name, "version": plugin.version},
                            source="plugin_bridge",
                        )

            return list(self._loaded_plugins.values())
        except ImportError:
            return []

    async def enable_plugin(self, name: str) -> dict[str, Any]:
        """Enable a loaded plugin."""
        if name not in self._loaded_plugins:
            raise OrchestratorError(f"Plugin '{name}' not loaded")
        self._loaded_plugins[name]["status"] = "enabled"
        if self._event_bus:
            await self._event_bus.publish(
                "plugin.enabled", {"name": name}, source="plugin_bridge",
            )
        return {"name": name, "status": "enabled"}

    async def disable_plugin(self, name: str) -> dict[str, Any]:
        """Disable a loaded plugin."""
        if name not in self._loaded_plugins:
            raise OrchestratorError(f"Plugin '{name}' not loaded")
        self._loaded_plugins[name]["status"] = "disabled"
        if self._event_bus:
            await self._event_bus.publish(
                "plugin.disabled", {"name": name}, source="plugin_bridge",
            )
        return {"name": name, "status": "disabled"}

    async def uninstall_plugin(self, name: str) -> dict[str, Any]:
        """Uninstall a plugin."""
        if name not in self._loaded_plugins:
            raise OrchestratorError(f"Plugin '{name}' not loaded")
        del self._loaded_plugins[name]
        if self._event_bus:
            await self._event_bus.publish(
                "plugin.uninstalled", {"name": name}, source="plugin_bridge",
            )
        return {"name": name, "status": "uninstalled"}

    def list_plugins(self, status: str = "") -> list[dict[str, Any]]:
        """List all plugins, optionally filtered."""
        plugins = list(self._loaded_plugins.values())
        if status:
            plugins = [p for p in plugins if p["status"] == status]
        return plugins

    def get_plugin(self, name: str) -> dict[str, Any] | None:
        """Get details for a specific plugin."""
        return self._loaded_plugins.get(name)

    def get_statistics(self) -> dict[str, Any]:
        """Get plugin statistics."""
        plugins = self._loaded_plugins.values()
        by_status: dict[str, int] = {}
        for p in plugins:
            by_status[p["status"]] = by_status.get(p["status"], 0) + 1
        return {
            "total_plugins": len(self._loaded_plugins),
            "by_status": by_status,
            "initialized": self._initialized,
        }
