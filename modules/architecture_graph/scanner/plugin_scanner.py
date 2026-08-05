"""Plugin scanner: discovers platform plugins and their manifests.

Scans the ``plugins/`` directory and the plugin manager SDK for manifest
files (plugin.json / manifest.json / plugin.yaml / plugin.yml) and registers
plugin nodes plus their declared dependencies.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MANIFEST_NAMES = ("plugin.json", "manifest.json", "plugin.yaml", "plugin.yml", "manifest.yaml")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return {}


def _plugin_from_dir(plugin_dir: Path) -> dict[str, Any] | None:
    for name in _MANIFEST_NAMES:
        manifest = plugin_dir / name
        if manifest.exists():
            if manifest.suffix in {".yaml", ".yml"}:
                from modules.architecture_graph.parsers.yaml_parser import parse as yaml_parse

                data = yaml_parse(manifest.read_text(encoding="utf-8", errors="ignore"))
            else:
                data = _read_json(manifest)
            return {
                "name": data.get("name") or plugin_dir.name,
                "path": plugin_dir.as_posix(),
                "version": data.get("version", ""),
                "dependencies": data.get("dependencies", []),
            }
    return None


def scan(root: str) -> list[dict[str, Any]]:
    """Scan the plugin directories and return discovered plugin records."""
    plugins: list[dict[str, Any]] = []
    candidates = [Path(root) / "plugins", Path(root) / "core" / "plugin_manager"]
    seen: set[str] = set()
    for base in candidates:
        if not base.exists():
            continue
        for entry in sorted(base.iterdir()):
            if not entry.is_dir() or entry.name.startswith((".", "_")):
                continue
            plugin = _plugin_from_dir(entry)
            if plugin and plugin["name"] not in seen:
                seen.add(plugin["name"])
                plugins.append(plugin)
    return plugins
