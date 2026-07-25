from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ..registry.plugin_registry import PluginRegistry


class PluginCleanup:
    def __init__(self, plugins_dir: str | Path, registry: PluginRegistry) -> None:
        self._plugins_dir = Path(plugins_dir).resolve()
        self._registry = registry
        self._cache_dir = self._plugins_dir.parent / ".cache"
        self._temp_dir = self._plugins_dir.parent / ".temp"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    def cleanup(self, name: str) -> None:
        plugin_cache = self._cache_dir / name
        if plugin_cache.exists():
            shutil.rmtree(plugin_cache)

        plugin_temp = self._temp_dir / name
        if plugin_temp.exists():
            shutil.rmtree(plugin_temp)

        plugin_dir = self._plugins_dir / name
        if plugin_dir.exists():
            pycache = plugin_dir / "__pycache__"
            if pycache.exists():
                shutil.rmtree(pycache)
            for pyc in plugin_dir.rglob("*.pyc"):
                pyc.unlink(missing_ok=True)

    def cleanup_all(self) -> None:
        registered_names = set()
        for entry in self._registry.list():
            registered_names.add(entry["name"])

        if self._cache_dir.exists():
            for item in self._cache_dir.iterdir():
                if item.is_dir() and item.name not in registered_names:
                    shutil.rmtree(item)

        if self._temp_dir.exists():
            for item in self._temp_dir.iterdir():
                if item.is_dir() and item.name not in registered_names:
                    shutil.rmtree(item)

        for plugin_dir in self._plugins_dir.iterdir():
            if plugin_dir.is_dir() and plugin_dir.name not in registered_names:
                pycache = plugin_dir / "__pycache__"
                if pycache.exists():
                    shutil.rmtree(pycache)
