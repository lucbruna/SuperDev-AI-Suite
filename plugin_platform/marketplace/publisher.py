from __future__ import annotations

import json
import os
import tarfile
import tempfile
from pathlib import Path
from typing import Any


class PluginPublisher:
    def __init__(self, store_path: str | None = None):
        self._store_path = Path(store_path or Path.home() / ".superdev" / "marketplace")
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._packages_dir = self._store_path / "packages"
        self._packages_dir.mkdir(parents=True, exist_ok=True)

    def _validate_manifest(self, manifest: dict[str, Any]) -> list[str]:
        errors = []
        required = ["name", "version", "description", "author"]
        for field in required:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")
        if "version" in manifest:
            parts = manifest["version"].split(".")
            if len(parts) != 3 or not all(p.isdigit() for p in parts):
                errors.append(f"Invalid version format: {manifest['version']} (expected semver)")
        return errors

    def create_package(self, plugin_dir: str, output: str | None = None) -> str:
        plugin_path = Path(plugin_dir)
        manifest_file = plugin_path / "manifest.json"
        if not manifest_file.exists():
            raise FileNotFoundError(f"manifest.json not found in {plugin_dir}")
        manifest = json.loads(manifest_file.read_text())
        errors = self._validate_manifest(manifest)
        if errors:
            raise ValueError(f"Invalid manifest: {'; '.join(errors)}")
        plugin_id = manifest.get("id", manifest["name"].lower().replace(" ", "-"))
        version = manifest["version"]
        package_name = f"{plugin_id}-{version}.tar.gz"
        output_path = Path(output) if output else self._packages_dir / package_name
        with tarfile.open(str(output_path), "w:gz") as tar:
            for file_path in plugin_path.rglob("*"):
                if file_path.is_file() and "__pycache__" not in str(file_path):
                    arcname = str(file_path.relative_to(plugin_path))
                    tar.add(str(file_path), arcname=arcname)
        return str(output_path)

    def publish(self, plugin_dir: str, api_key: str, api_url: str = "https://marketplace.superdev.ai/api/v1") -> dict[str, Any]:
        from cli.client import APIClient
        package_path = self.create_package(plugin_dir)
        client = APIClient()
        import httpx
        with open(package_path, "rb") as f:
            response = httpx.post(
                f"{api_url}/plugins/publish",
                files={"package": ("package.tar.gz", f, "application/gzip")},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60,
            )
            response.raise_for_status()
            return response.json()

    def publish_local(self, plugin_dir: str, store: Any | None = None) -> dict[str, Any]:
        from .store import PluginStore
        store = store or PluginStore()
        plugin_path = Path(plugin_dir)
        manifest_file = plugin_path / "manifest.json"
        if not manifest_file.exists():
            raise FileNotFoundError(f"manifest.json not found in {plugin_dir}")
        manifest = json.loads(manifest_file.read_text())
        errors = self._validate_manifest(manifest)
        if errors:
            raise ValueError(f"Invalid manifest: {'; '.join(errors)}")
        plugin_id = store.add(manifest)
        package_path = self.create_package(plugin_dir)
        return {"id": plugin_id, "package_path": package_path, "manifest": manifest}

    def generate_manifest(self, name: str, description: str, author: str, version: str = "1.0.0", category: str = "tool") -> dict[str, Any]:
        return {
            "name": name,
            "id": name.lower().replace(" ", "-"),
            "version": version,
            "description": description,
            "author": author,
            "category": category,
            "tags": [],
            "license": "MIT",
            "min_superdev_version": "0.1.0",
            "entry": "main.py",
            "dependencies": [],
        }

    def save_manifest(self, manifest: dict[str, Any], output_dir: str) -> str:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        manifest_file = output_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2))
        return str(manifest_file)