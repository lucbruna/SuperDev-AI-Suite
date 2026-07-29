import os, pathlib

BASE = pathlib.Path(r"C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\plugin_platform")

files = {}

files["registry/plugin_registry.py"] = r'''from __future__ import annotations

import fnmatch
from typing import Any


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, dict[str, Any]] = {}

    def register(self, name: str, manifest: dict[str, Any], plugin_class: type) -> None:
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' is already registered")
        self._plugins[name] = {
            "name": name,
            "manifest": manifest,
            "plugin_class": plugin_class,
            "enabled": True,
        }

    def unregister(self, name: str) -> None:
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found")
        del self._plugins[name]

    def get(self, name: str) -> dict[str, Any] | None:
        entry = self._plugins.get(name)
        if entry is None:
            return None
        return {
            "name": entry["name"],
            "manifest": entry["manifest"],
            "enabled": entry["enabled"],
        }

    def list(self, category: str | None = None) -> list[dict[str, Any]]:
        results = []
        for entry in self._plugins.values():
            manifest = entry["manifest"]
            if category is None or manifest.get("category") == category:
                results.append({
                    "name": entry["name"],
                    "manifest": manifest,
                    "enabled": entry["enabled"],
                })
        return results

    def find(self, query: str) -> list[dict[str, Any]]:
        results = []
        q = query.lower()
        for entry in self._plugins.values():
            manifest = entry["manifest"]
            if (
                q in entry["name"].lower()
                or q in manifest.get("description", "").lower()
                or q in manifest.get("author", "").lower()
            ):
                results.append({
                    "name": entry["name"],
                    "manifest": manifest,
                    "enabled": entry["enabled"],
                })
        return results

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        return self.list(category=category)
'''

files["registry/provider_registry.py"] = r'''from __future__ import annotations

from typing import Any


class ProviderPluginRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, type] = {}

    def register_provider(self, name: str, provider_class: type) -> None:
        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered")
        self._providers[name] = provider_class

    def get_provider(self, name: str) -> type | None:
        return self._providers.get(name)

    def list_providers(self) -> list[dict[str, Any]]:
        return [
            {"name": name, "provider_class": cls}
            for name, cls in self._providers.items()
        ]
'''

files["loader/plugin_loader.py"] = r'''from __future__ import annotations

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
'''

files["loader/module_loader.py"] = r'''from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


class ModuleLoader:
    def __init__(self) -> None:
        self._modules: dict[str, ModuleType] = {}

    def import_module(self, path: str | Path) -> ModuleType:
        module_path = Path(path).resolve()
        if not module_path.exists():
            raise FileNotFoundError(f"Module not found: {module_path}")

        module_name = module_path.stem
        if module_name in sys.modules:
            return sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, str(module_path))
        if spec is None:
            raise ImportError(f"Could not load spec from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        if spec.loader:
            spec.loader.exec_module(module)

        self._modules[module_name] = module
        return module

    def get_module(self, name: str) -> ModuleType | None:
        return self._modules.get(name) or sys.modules.get(name)

    def reload_module(self, name: str) -> ModuleType:
        if name in sys.modules:
            module = importlib.reload(sys.modules[name])
            self._modules[name] = module
            return module
        raise ImportError(f"Module '{name}' is not loaded")
'''

files["loader/hot_reload.py"] = r'''from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Callable


class HotReloader:
    def __init__(self, poll_interval: float = 1.0) -> None:
        self._poll_interval = poll_interval
        self._watchers: dict[str, tuple[str, float, Callable[[str], None], threading.Thread, threading.Event]] = {}
        self._running = False

    def watch(self, plugin_path: str | Path, callback: Callable[[str], None]) -> None:
        path = Path(plugin_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {plugin_path}")

        path_str = str(path)
        if path_str in self._watchers:
            raise ValueError(f"Already watching: {plugin_path}")

        last_mtime = self._get_mtime(path)
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self._poll_loop,
            args=(path_str, last_mtime, callback, stop_event),
            daemon=True,
        )
        self._watchers[path_str] = (path_str, last_mtime, callback, thread, stop_event)
        self._running = True
        thread.start()

    def _get_mtime(self, path: Path) -> float:
        if path.is_file():
            return os.path.getmtime(path)
        max_mtime = 0.0
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                mtime = os.path.getmtime(fp)
                if mtime > max_mtime:
                    max_mtime = mtime
        return max_mtime

    def _poll_loop(self, path_str: str, last_mtime: float, callback: Callable[[str], None], stop_event: threading.Event) -> None:
        while not stop_event.is_set():
            time.sleep(self._poll_interval)
            current_mtime = self._get_mtime(Path(path_str))
            if current_mtime > last_mtime:
                last_mtime = current_mtime
                self._watchers[path_str] = (path_str, last_mtime, callback, self._watchers[path_str][3], stop_event)
                callback(path_str)

    def stop(self) -> None:
        for key in list(self._watchers.keys()):
            path_str, last_mtime, callback, thread, stop_event = self._watchers[key]
            stop_event.set()
            thread.join(timeout=2.0)
        self._watchers.clear()
        self._running = False
'''

files["installer/install.py"] = r'''from __future__ import annotations

import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from ..registry.plugin_registry import PluginRegistry
from ..validator.manifest_validator import ManifestValidator


class PluginInstaller:
    def __init__(self, plugins_dir: str | Path, registry: PluginRegistry) -> None:
        self._plugins_dir = Path(plugins_dir).resolve()
        self._registry = registry
        self._manifest_validator = ManifestValidator()
        self._plugins_dir.mkdir(parents=True, exist_ok=True)

    def install(self, source: str | Path) -> dict[str, Any]:
        source = Path(source)
        temp_dir = None

        try:
            if source.is_dir():
                manifest = self._install_from_dir(source)
            elif source.suffix == ".zip":
                manifest = self._install_from_zip(source)
            elif source.suffix in (".yaml", ".yml"):
                manifest = self._install_from_manifest(source)
            else:
                raise ValueError(f"Unsupported source: {source}")
            return manifest
        finally:
            if temp_dir is not None:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _install_from_dir(self, source: Path) -> dict[str, Any]:
        manifest_file = self._find_manifest(source)
        manifest = self._load_and_validate(manifest_file)
        name = manifest["name"]
        target_dir = self._plugins_dir / name
        if target_dir.exists():
            raise FileExistsError(f"Plugin '{name}' is already installed at {target_dir}")
        shutil.copytree(source, target_dir)
        manifest["_manifest_path"] = str(target_dir / manifest_file.name)
        self._registry.register(name, manifest, type("Plugin", (object,), {"__plugin_name__": name}))
        return manifest

    def _install_from_zip(self, source: Path) -> dict[str, Any]:
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(source, "r") as zf:
                zf.extractall(tmp)
            extracted = Path(tmp)
            manifest_file = self._find_manifest(extracted)
            return self._install_from_manifest(manifest_file)

    def _install_from_manifest(self, manifest_file: Path) -> dict[str, Any]:
        manifest_dir = manifest_file.parent
        manifest = self._load_and_validate(manifest_file)
        name = manifest["name"]
        target_dir = self._plugins_dir / name
        if target_dir.exists():
            raise FileExistsError(f"Plugin '{name}' is already installed at {target_dir}")
        shutil.copytree(manifest_dir, target_dir)
        manifest["_manifest_path"] = str(target_dir / manifest_file.name)
        self._registry.register(name, manifest, type("Plugin", (object,), {"__plugin_name__": name}))
        return manifest

    def _find_manifest(self, directory: Path) -> Path:
        for name in ("plugin.yaml", "plugin.yml", "plugin.superdev.yaml"):
            candidate = directory / name
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"No manifest file found in {directory}")

    def _load_and_validate(self, manifest_file: Path) -> dict[str, Any]:
        import yaml
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        if not isinstance(manifest, dict):
            raise ValueError("Invalid manifest")
        result = self._manifest_validator.validate(manifest)
        if not result.success:
            raise ValueError(f"Manifest validation failed: {result.errors}")
        manifest["_manifest_path"] = str(manifest_file)
        return manifest
'''

files["installer/uninstall.py"] = r'''from __future__ import annotations

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
'''

files["installer/upgrade.py"] = r'''from __future__ import annotations

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
'''

files["installer/rollback.py"] = r'''from __future__ import annotations

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
'''

files["installer/cleanup.py"] = r'''from __future__ import annotations

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
'''

files["validator/manifest_validator.py"] = r'''from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..manifest.defaults import DEFAULT_CATEGORY


@dataclass
class ValidationResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ManifestValidator:
    VALID_CATEGORIES = {"tool", "provider", "agent", "theme", "language", "other"}
    ALLOWED_PERMISSIONS = {
        "filesystem.read", "filesystem.write", "network.http", "network.all",
        "process.spawn", "clipboard.read", "clipboard.write", "ui.notification",
        "storage.local", "storage.global",
    }

    def __init__(self) -> None:
        self._semver_pattern = re.compile(
            r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
            r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
            r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
            r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        )

    def validate(self, manifest: dict[str, Any]) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        name = manifest.get("name")
        if not name or not isinstance(name, str):
            errors.append("Manifest 'name' is required and must be a non-empty string")
        elif not name.strip():
            errors.append("Manifest 'name' must not be empty or whitespace-only")

        version = manifest.get("version")
        if not version or not isinstance(version, str):
            errors.append("Manifest 'version' is required and must be a string")
        elif not self._semver_pattern.match(version):
            errors.append(f"Manifest 'version' '{version}' is not valid semver")

        entrypoint = manifest.get("entrypoint")
        if entrypoint is not None:
            if not isinstance(entrypoint, str):
                errors.append("Manifest 'entrypoint' must be a string")
            elif not entrypoint.strip():
                errors.append("Manifest 'entrypoint' must not be empty")

        permissions = manifest.get("permissions", [])
        if not isinstance(permissions, list):
            errors.append("Manifest 'permissions' must be a list")
        else:
            for perm in permissions:
                if perm not in self.ALLOWED_PERMISSIONS:
                    warnings.append(f"Permission '{perm}' is not in the allowed list")

        category = manifest.get("category", DEFAULT_CATEGORY)
        if category not in self.VALID_CATEGORIES:
            warnings.append(f"Category '{category}' is not standard; valid: {self.VALID_CATEGORIES}")

        author = manifest.get("author")
        if author is not None and not isinstance(author, str):
            errors.append("Manifest 'author' must be a string")

        description = manifest.get("description")
        if description is not None and not isinstance(description, str):
            errors.append("Manifest 'description' must be a string")

        dependencies = manifest.get("dependencies")
        if dependencies is not None:
            if not isinstance(dependencies, list):
                errors.append("Manifest 'dependencies' must be a list")

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)
'''

files["validator/dependency_validator.py"] = r'''from __future__ import annotations

from typing import Any


class DependencyValidator:
    def check_dependencies(
        self, manifest: dict[str, Any], installed_plugins: dict[str, dict[str, Any]]
    ) -> list[tuple[str, bool, str]]:
        results: list[tuple[str, bool, str]] = []
        dependencies = manifest.get("dependencies", [])

        if not dependencies:
            return results

        for dep in dependencies:
            if isinstance(dep, str):
                dep_name = dep
                dep_version = None
            elif isinstance(dep, dict):
                dep_name = dep.get("name", "")
                dep_version = dep.get("version")
            else:
                results.append((str(dep), False, f"Invalid dependency format: {dep}"))
                continue

            if not dep_name:
                results.append(("unknown", False, "Dependency name is empty"))
                continue

            if dep_name not in installed_plugins:
                results.append((dep_name, False, f"Dependency '{dep_name}' is not installed"))
                continue

            if dep_version:
                installed_manifest = installed_plugins[dep_name].get("manifest", {})
                installed_version = installed_manifest.get("version", "0.0.0")
                if self._compare_versions(installed_version, dep_version) < 0:
                    results.append((
                        dep_name, False,
                        f"Dependency '{dep_name}' version {installed_version} < required {dep_version}"
                    ))
                    continue

            results.append((dep_name, True, f"Dependency '{dep_name}' is satisfied"))

        return results

    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        def parse(v: str) -> tuple[int, ...]:
            parts = v.split(".")[:3]
            return tuple(int(p) if p.isdigit() else 0 for p in parts)
        p1 = parse(v1)
        p2 = parse(v2)
        if p1 < p2:
            return -1
        if p1 > p2:
            return 1
        return 0
'''

files["validator/compatibility_validator.py"] = r'''from __future__ import annotations

import platform
import sys
from typing import Any


class CompatibilityValidator:
    MIN_PYTHON = (3, 11)
    MIN_SUPERDEV = (5, 0, 0)
    SUPPORTED_PLATFORMS = {"windows", "linux", "darwin", "win32", "win64"}

    def check(self, manifest: dict[str, Any]) -> list[tuple[str, bool, str]]:
        results: list[tuple[str, bool, str]] = []

        python_version = sys.version_info[:2]
        if python_version >= self.MIN_PYTHON:
            results.append((
                "python_version", True,
                f"Python {python_version[0]}.{python_version[1]} >= {self.MIN_PYTHON[0]}.{self.MIN_PYTHON[1]}"
            ))
        else:
            results.append((
                "python_version", False,
                f"Python {python_version[0]}.{python_version[1]} < {self.MIN_PYTHON[0]}.{self.MIN_PYTHON[1]}"
            ))

        superdev_version_str = manifest.get("superdev_version")
        if superdev_version_str:
            try:
                parts = tuple(int(x) for x in superdev_version_str.split(".")[:3])
                if parts >= self.MIN_SUPERDEV:
                    results.append((
                        "superdev_version", True,
                        f"SuperDev {superdev_version_str} >= {'.'.join(str(x) for x in self.MIN_SUPERDEV)}"
                    ))
                else:
                    results.append((
                        "superdev_version", False,
                        f"SuperDev {superdev_version_str} < {'.'.join(str(x) for x in self.MIN_SUPERDEV)}"
                    ))
            except ValueError:
                results.append(("superdev_version", False, f"Invalid superdev_version: {superdev_version_str}"))
        else:
            results.append(("superdev_version", True, "No superdev_version specified, assuming compatible"))

        required_platform = manifest.get("platform")
        if required_platform:
            current_platform = platform.system().lower()
            if current_platform in self.SUPPORTED_PLATFORMS:
                current_platform = current_platform.replace("win32", "windows").replace("win64", "windows")
            if required_platform.lower() == current_platform:
                results.append(("platform", True, f"Platform '{current_platform}' matches required '{required_platform}'"))
            else:
                results.append(("platform", False, f"Platform '{current_platform}' does not match required '{required_platform}'"))
        else:
            results.append(("platform", True, "No platform restriction specified"))

        extra_requires = manifest.get("extra_requires", {})
        if isinstance(extra_requires, dict):
            for extra_name, extra_version in extra_requires.items():
                try:
                    __import__(extra_name)
                    results.append((f"extra_{extra_name}", True, f"Extra dependency '{extra_name}' is available"))
                except ImportError:
                    results.append((f"extra_{extra_name}", False, f"Extra dependency '{extra_name}' is not installed"))

        return results
'''

print("Writing files...")
for relpath, content in files.items():
    fullpath = BASE / relpath
    fullpath.parent.mkdir(parents=True, exist_ok=True)
    fullpath.write_text(content, encoding="utf-8")
    print(f"  Wrote {relpath}")

print("Done writing registry, loader, installer, validator files")