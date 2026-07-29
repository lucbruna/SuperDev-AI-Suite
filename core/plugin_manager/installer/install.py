from __future__ import annotations

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
