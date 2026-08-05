"""Plugin discovery: locate plugin manifests and map them to graph nodes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modules.architecture_graph.mappers.plugin_registry import PluginRegistry
from modules.architecture_graph.scanner.plugin_scanner import _MANIFEST_NAMES, scan

_MANIFEST_CONTENT_EXTS = {".json", ".yaml", ".yml"}


class PluginDiscovery:
    """Deep plugin discovery including manifest content details."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.registry = PluginRegistry(root)

    def discover_manifests(self) -> list[dict[str, Any]]:
        """List every plugin manifest file with its raw content summary."""
        base = Path(self.root)
        candidates = [base / "plugins", base / "core" / "plugin_manager"]
        results: list[dict[str, Any]] = []
        for root_dir in candidates:
            if not root_dir.exists():
                continue
            for manifest in sorted(root_dir.rglob("*")):
                if manifest.name not in _MANIFEST_NAMES:
                    continue
                if manifest.suffix not in _MANIFEST_CONTENT_EXTS:
                    continue
                try:
                    text = manifest.read_text(encoding="utf-8", errors="ignore")[:50_000]
                except OSError:
                    continue
                parsed: dict[str, Any] = {}
                if manifest.suffix == ".json":
                    try:
                        parsed = json.loads(text)
                    except ValueError:
                        parsed = {"parse_error": True}
                else:
                    from modules.architecture_graph.parsers.yaml_parser import (
                        parse as yaml_parse,
                    )

                    parsed = yaml_parse(text)
                results.append(
                    {
                        "path": manifest.relative_to(base).as_posix(),
                        "plugin_dir": manifest.parent.name,
                        "name": parsed.get("name") or manifest.parent.name,
                        "version": parsed.get("version", ""),
                        "dependencies": parsed.get("dependencies", []),
                    }
                )
        results.sort(key=lambda r: r["path"])
        return results

    def summary(self) -> dict[str, Any]:
        plugins = scan(self.root)
        manifests = self.discover_manifests()
        return {
            "plugins": len(plugins),
            "manifests": len(manifests),
            "with_dependencies": sum(
                1 for m in manifests if m.get("dependencies")
            ),
        }
