from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

from backend.plugins.base_plugin import (
    BasePlugin,
    PluginConfig,
    PluginMetadata,
    PluginStatus,
    PluginType,
)
from backend.utils.uuid_utils import generate_uuid


class PluginManager:
    """Manages plugin installation, lifecycle, and execution."""

    def __init__(self, plugins_dir: str = "plugins"):
        self._plugins: dict[str, BasePlugin] = {}
        self._plugins_dir = Path(plugins_dir)
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self._plugins_dir / "plugins.json"
        self._load_config()

    def _load_config(self) -> None:
        if self._config_file.exists():
            with open(self._config_file) as f:
                self._config_data = json.load(f)
        else:
            self._config_data = {"installed": {}}

    def _save_config(self) -> None:
        with open(self._config_file, "w") as f:
            json.dump(self._config_data, f, indent=2)

    async def install_plugin(
        self,
        metadata: PluginMetadata,
        plugin_class: type[BasePlugin],
        config: PluginConfig | None = None,
    ) -> BasePlugin:
        plugin_id = generate_uuid()

        if metadata.slug in self._plugins:
            raise ValueError(f"Plugin already installed: {metadata.slug}")

        plugin = plugin_class(metadata=metadata, config=config)

        self._plugins[metadata.slug] = plugin

        self._config_data["installed"][metadata.slug] = {
            "id": plugin_id,
            "name": metadata.name,
            "version": metadata.version,
            "enabled": True,
        }
        self._save_config()

        await plugin.activate()
        return plugin

    async def uninstall_plugin(self, slug: str) -> bool:
        plugin = self._plugins.get(slug)
        if not plugin:
            return False

        await plugin.deactivate()
        del self._plugins[slug]

        if slug in self._config_data["installed"]:
            del self._config_data["installed"][slug]
            self._save_config()

        plugin_dir = self._plugins_dir / slug
        if plugin_dir.exists():
            import shutil
            shutil.rmtree(plugin_dir)

        return True

    async def enable_plugin(self, slug: str) -> bool:
        plugin = self._plugins.get(slug)
        if not plugin:
            return False

        await plugin.activate()

        if slug in self._config_data["installed"]:
            self._config_data["installed"][slug]["enabled"] = True
            self._save_config()

        return True

    async def disable_plugin(self, slug: str) -> bool:
        plugin = self._plugins.get(slug)
        if not plugin:
            return False

        await plugin.deactivate()

        if slug in self._config_data["installed"]:
            self._config_data["installed"][slug]["enabled"] = False
            self._save_config()

        return True

    def get_plugin(self, slug: str) -> BasePlugin | None:
        return self._plugins.get(slug)

    def list_plugins(self, plugin_type: PluginType | None = None) -> list[dict[str, Any]]:
        plugins = list(self._plugins.values())
        if plugin_type:
            plugins = [p for p in plugins if p.metadata.plugin_type == plugin_type]
        return [p.to_dict() for p in plugins]

    def get_installed_slugs(self) -> list[str]:
        return list(self._config_data.get("installed", {}).keys())

    async def update_plugin_config(self, slug: str, settings: dict[str, Any]) -> bool:
        plugin = self._plugins.get(slug)
        if not plugin:
            return False

        await plugin.on_config_change(settings)

        if slug in self._config_data["installed"]:
            self._config_data["installed"][slug]["settings"] = settings
            self._save_config()

        return True

    def get_plugin_api(self, slug: str) -> dict[str, Any] | None:
        plugin = self._plugins.get(slug)
        return plugin.get_api() if plugin else None

    async def trigger_hook(self, hook_name: str, **kwargs) -> dict[str, list[Any]]:
        results = {}
        for slug, plugin in self._plugins.items():
            if plugin.status == PluginStatus.ENABLED:
                try:
                    hook_results = await plugin.trigger_hook(hook_name, **kwargs)
                    results[slug] = hook_results
                except Exception as e:
                    results[slug] = [{"error": str(e)}]
        return results

    async def validate_plugin(self, metadata: PluginMetadata) -> list[str]:
        errors = []

        if not metadata.name:
            errors.append("Plugin name is required")
        if not metadata.slug:
            errors.append("Plugin slug is required")
        if not metadata.version:
            errors.append("Plugin version is required")

        for dep in metadata.dependencies:
            if dep not in self._plugins:
                errors.append(f"Missing dependency: {dep}")

        return errors


plugin_manager = PluginManager()
