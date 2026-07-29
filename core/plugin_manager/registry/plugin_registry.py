from __future__ import annotations

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
