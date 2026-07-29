from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class PluginStore:
    def __init__(self, store_path: str | None = None):
        self._store_path = Path(store_path or Path.home() / ".superdev" / "marketplace")
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._plugins: dict[str, dict[str, Any]] = {}
        self._categories: dict[str, list[str]] = {}
        self._load()

    def _load(self):
        plugins_file = self._store_path / "plugins.json"
        if plugins_file.exists():
            try:
                data = json.loads(plugins_file.read_text())
                self._plugins = data.get("plugins", {})
                self._categories = data.get("categories", {})
            except (json.JSONDecodeError, KeyError):
                pass
        if not self._plugins:
            self._seed_defaults()

    def _save(self):
        data = {"plugins": self._plugins, "categories": self._categories}
        (self._store_path / "plugins.json").write_text(json.dumps(data, indent=2, default=str))

    def _seed_defaults(self):
        defaults = [
            {"id": "text-formatter", "name": "Text Formatter", "version": "1.2.0", "author": "SuperDev Team", "description": "Format and beautify text content", "category": "tool", "downloads": 1520, "rating": 4.5, "tags": ["text", "format"], "install_count": 320},
            {"id": "ai-assistant", "name": "AI Assistant Provider", "version": "2.0.1", "author": "SuperDev Team", "description": "AI-powered code assistance provider", "category": "provider", "downloads": 3400, "rating": 4.8, "tags": ["ai", "provider"], "install_count": 890},
            {"id": "code-analyzer", "name": "Code Analyzer Agent", "version": "1.0.0", "author": "Community", "description": "Static code analysis agent", "category": "agent", "downloads": 890, "rating": 4.2, "tags": ["code", "analysis"], "install_count": 210},
            {"id": "slack-notifier", "name": "Slack Notifier", "version": "1.1.0", "author": "SuperDev Team", "description": "Send notifications to Slack channels", "category": "integration", "downloads": 2100, "rating": 4.6, "tags": ["slack", "notification"], "install_count": 540},
            {"id": "github-sync", "name": "GitHub Sync", "version": "1.0.0", "author": "Community", "description": "Sync workflows with GitHub repositories", "category": "integration", "downloads": 1560, "rating": 4.4, "tags": ["github", "sync"], "install_count": 410},
            {"id": "docker-deploy", "name": "Docker Deploy", "version": "0.9.0", "author": "Community", "description": "Deploy agents in Docker containers", "category": "runtime", "downloads": 780, "rating": 3.9, "tags": ["docker", "deploy"], "install_count": 180},
        ]
        for p in defaults:
            self._plugins[p["id"]] = p
            cat = p.get("category", "uncategorized")
            if cat not in self._categories:
                self._categories[cat] = []
            if p["id"] not in self._categories[cat]:
                self._categories[cat].append(p["id"])
        self._save()

    def add(self, plugin: dict[str, Any]) -> str:
        plugin_id = plugin.get("id", plugin.get("name", "").lower().replace(" ", "-"))
        plugin["id"] = plugin_id
        self._plugins[plugin_id] = plugin
        cat = plugin.get("category", "uncategorized")
        if cat not in self._categories:
            self._categories[cat] = []
        if plugin_id not in self._categories[cat]:
            self._categories[cat].append(plugin_id)
        self._save()
        return plugin_id

    def get(self, plugin_id: str) -> dict[str, Any] | None:
        return self._plugins.get(plugin_id)

    def remove(self, plugin_id: str) -> None:
        plugin = self._plugins.pop(plugin_id, None)
        if plugin:
            cat = plugin.get("category", "uncategorized")
            cat_list = self._categories.get(cat, [])
            if plugin_id in cat_list:
                cat_list.remove(plugin_id)
            self._save()

    def update(self, plugin_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        plugin = self._plugins.get(plugin_id)
        if plugin:
            plugin.update(updates)
            self._save()
        return plugin

    def increment_downloads(self, plugin_id: str) -> None:
        plugin = self._plugins.get(plugin_id)
        if plugin:
            plugin["downloads"] = plugin.get("downloads", 0) + 1
            self._save()

    def increment_installs(self, plugin_id: str) -> None:
        plugin = self._plugins.get(plugin_id)
        if plugin:
            plugin["install_count"] = plugin.get("install_count", 0) + 1
            self._save()

    def search(self, query: str = "", category: str = "", tag: str = "", sort: str = "downloads") -> list[dict[str, Any]]:
        results = list(self._plugins.values())
        if query:
            q = query.lower()
            results = [p for p in results if q in p.get("name", "").lower() or q in p.get("description", "").lower() or q in p.get("author", "").lower()]
        if category:
            results = [p for p in results if p.get("category") == category]
        if tag:
            results = [p for p in results if tag in p.get("tags", [])]
        if sort == "downloads":
            results.sort(key=lambda p: p.get("downloads", 0), reverse=True)
        elif sort == "rating":
            results.sort(key=lambda p: p.get("rating", 0), reverse=True)
        elif sort == "name":
            results.sort(key=lambda p: p.get("name", ""))
        return results

    def get_categories(self) -> list[dict[str, Any]]:
        result = []
        for cat, plugins in self._categories.items():
            count = len(plugins)
            result.append({"id": cat, "name": cat.capitalize(), "count": count})
        return sorted(result, key=lambda c: c["count"], reverse=True)

    def get_featured(self, limit: int = 6) -> list[dict[str, Any]]:
        all_plugins = sorted(self._plugins.values(), key=lambda p: p.get("downloads", 0), reverse=True)
        return all_plugins[:limit]

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_plugins": len(self._plugins),
            "total_categories": len(self._categories),
            "total_downloads": sum(p.get("downloads", 0) for p in self._plugins.values()),
            "total_installs": sum(p.get("install_count", 0) for p in self._plugins.values()),
        }

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._plugins.values())