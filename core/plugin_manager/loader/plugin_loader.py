from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

from ..registry.plugin_registry import PluginRegistry
from ..loader.module_loader import ModuleLoader


class PluginLoader:
    def __init__(self, registry: PluginRegistry, module_loader: ModuleLoader | None = None) -> None:
        self._registry = registry
        self._module_loader = module_loader or ModuleLoader()

    def load_plugin(self, manifest_path: str | Path) -> dict[str, Any]:
        manifest_path = Path(manifest_path).resolve()
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        import yaml
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        if not isinstance(manifest, dict):
            raise ValueError("Invalid manifest format")

        name = manifest.get("name")
        if not name:
            raise ValueError("Manifest must contain a 'name' field")

        entrypoint = manifest.get("entrypoint", "plugin.py")
        plugin_dir = manifest_path.parent
        module_path = plugin_dir / entrypoint

        module = self._module_loader.import_module(str(module_path))

        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and hasattr(attr, "__plugin_name__"):
                plugin_class = attr
                break

        if plugin_class is None:
            plugin_class_name = manifest.get("plugin_class", "Plugin")
            if hasattr(module, plugin_class_name):
                plugin_class = getattr(module, plugin_class_name)

        if plugin_class is None:
            plugin_class = type("Plugin", (object,), {"__plugin_name__": name})

        self._registry.register(name, manifest, plugin_class)
        return self._registry.get(name) or {"name": name, "manifest": manifest, "enabled": True}

    def unload(self, name: str) -> None:
        entry = self._registry.get(name)
        if entry is None:
            raise KeyError(f"Plugin '{name}' is not loaded")
        self._registry.unregister(name)

    def reload(self, name: str) -> dict[str, Any]:
        entry = self._registry.get(name)
        if entry is None:
            raise KeyError(f"Plugin '{name}' is not loaded")

        manifest = entry["manifest"]
        self._registry.unregister(name)

        module_name = f"plugin_{name}"
        if module_name in sys.modules:
            del sys.modules[module_name]

        return self.load_plugin(manifest.get("_manifest_path", ""))
