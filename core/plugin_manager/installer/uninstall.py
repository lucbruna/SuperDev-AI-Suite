from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from ..registry.plugin_registry import PluginRegistry


class PluginUninstaller:
    def __init__(self, plugins_dir: str | Path, registry: PluginRegistry) -> None:
        self._plugins_dir = Path(plugins_dir).resolve()
        self._registry = registry

    def uninstall(self, name: str) -> bool:
        entry = self._registry.get(name)
        if entry is None:
            return False

        plugin_dir = self._plugins_dir / name
        if plugin_dir.exists():
            self._cleanup_plugin_dir(plugin_dir)

        self._registry.unregister(name)
        return True

    def _cleanup_plugin_dir(self, plugin_dir: Path) -> None:
        for item in plugin_dir.iterdir():
            if item.is_dir() and item.name in ("__pycache__", ".git", ".venv"):
                shutil.rmtree(item, ignore_errors=True)
            elif item.suffix in (".pyc", ".pyo"):
                item.unlink(missing_ok=True)

        shutil.rmtree(plugin_dir, ignore_errors=True)
