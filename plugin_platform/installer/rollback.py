from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ..registry.plugin_registry import PluginRegistry


class PluginRollback:
    def __init__(self, plugins_dir: str | Path, registry: PluginRegistry, backup_dir: str | Path | None = None) -> None:
        self._plugins_dir = Path(plugins_dir).resolve()
        self._registry = registry
        self._backup_dir = Path(backup_dir) if backup_dir else self._plugins_dir.parent / ".backups"
        self._backup_dir.mkdir(parents=True, exist_ok=True)

    def rollback(self, name: str, version: str) -> bool:
        backup_path = self._backup_dir / f"{name}__{version}"
        if not backup_path.exists():
            raise FileNotFoundError(f"No backup found for plugin '{name}' version {version}")

        metadata_file = backup_path / ".metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Backup metadata missing for '{name}' version {version}")

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        plugin_dir = self._plugins_dir / name
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)
        shutil.copytree(backup_path, plugin_dir)
        shutil.rmtree(backup_path)

        manifest = metadata.get("manifest", {})
        entry = self._registry.get(name)
        if entry:
            plugin_class = entry["plugin_class"]
            self._registry.unregister(name)
            self._registry.register(name, manifest, plugin_class)
        else:
            self._registry.register(name, manifest, type("Plugin", (object,), {"__plugin_name__": name}))

        return True

    def create_backup(self, name: str, manifest: dict[str, Any]) -> Path:
        plugin_dir = self._plugins_dir / name
        if not plugin_dir.exists():
            raise FileNotFoundError(f"Plugin directory not found: {plugin_dir}")
        version = manifest.get("version", "0.0.0")
        backup_path = self._backup_dir / f"{name}__{version}"
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(plugin_dir, backup_path)
        metadata = {"name": name, "version": version, "manifest": manifest}
        with open(backup_path / ".metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        return backup_path
