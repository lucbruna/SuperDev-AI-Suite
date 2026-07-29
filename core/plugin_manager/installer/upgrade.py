from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ..registry.plugin_registry import PluginRegistry
from ..installer.install import PluginInstaller


class PluginUpgrader:
    def __init__(self, plugins_dir: str | Path, registry: PluginRegistry, installer: PluginInstaller) -> None:
        self._plugins_dir = Path(plugins_dir).resolve()
        self._registry = registry
        self._installer = installer

    def upgrade(self, name: str, new_version: str) -> bool:
        entry = self._registry.get(name)
        if entry is None:
            raise KeyError(f"Plugin '{name}' is not installed")

        old_manifest = entry["manifest"]
        old_version = old_manifest.get("version", "0.0.0")

        if new_version == old_version:
            return False

        plugin_dir = self._plugins_dir / name
        backup_dir = None

        try:
            backup_dir = Path(tempfile.mkdtemp()) / name
            if plugin_dir.exists():
                shutil.copytree(plugin_dir, backup_dir)

            source_path = self._download_upgrade(name, new_version)
            plugin_dir_new = plugin_dir.with_name(f"{name}_new")
            if plugin_dir_new.exists():
                shutil.rmtree(plugin_dir_new)

            import zipfile
            with zipfile.ZipFile(source_path, "r") as zf:
                zf.extractall(plugin_dir_new)

            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            plugin_dir_new.rename(plugin_dir)

            new_manifest = old_manifest.copy()
            new_manifest["version"] = new_version
            self._run_migration(name, old_version, new_version)

            self._registry.unregister(name)
            self._registry.register(name, new_manifest, entry["plugin_class"])
            return True

        except Exception:
            if backup_dir and backup_dir.exists():
                if plugin_dir.exists():
                    shutil.rmtree(plugin_dir)
                shutil.copytree(backup_dir, plugin_dir)
            raise

        finally:
            if backup_dir and backup_dir.parent.exists():
                shutil.rmtree(backup_dir.parent, ignore_errors=True)

    def _download_upgrade(self, name: str, version: str) -> Path:
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".zip")
        import os
        os.close(fd)
        p = Path(path)
        p.write_text(json.dumps({"name": name, "version": version}))
        return p

    def _run_migration(self, name: str, old_version: str, new_version: str) -> None:
        plugin_dir = self._plugins_dir / name
        migration_script = plugin_dir / "migration.py"
        if migration_script.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"migration_{name}", str(migration_script))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "migrate"):
                    module.migrate(old_version, new_version)
