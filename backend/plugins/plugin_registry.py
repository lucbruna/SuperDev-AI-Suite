from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PluginEntry:
    name: str
    slug: str
    version: str
    description: str
    author: str
    plugin_type: str
    tags: list[str] = field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    is_official: bool = False
    repository_url: str = ""
    homepage_url: str = ""


class PluginRegistry:
    """Marketplace registry for available plugins."""

    def __init__(self):
        self._plugins: dict[str, PluginEntry] = {}

    def register(self, entry: PluginEntry) -> None:
        self._plugins[entry.slug] = entry

    def get(self, slug: str) -> PluginEntry | None:
        return self._plugins.get(slug)

    def list_plugins(
        self,
        plugin_type: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        sort_by: str = "downloads",
        limit: int = 50,
    ) -> list[PluginEntry]:
        plugins = list(self._plugins.values())

        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]
        if tag:
            plugins = [p for p in plugins if tag in p.tags]
        if search:
            search_lower = search.lower()
            plugins = [
                p for p in plugins
                if search_lower in p.name.lower()
                or search_lower in p.description.lower()
                or search_lower in p.slug.lower()
            ]

        if sort_by == "downloads":
            plugins.sort(key=lambda p: p.downloads, reverse=True)
        elif sort_by == "rating":
            plugins.sort(key=lambda p: p.rating, reverse=True)
        elif sort_by == "name":
            plugins.sort(key=lambda p: p.name)

        return plugins[:limit]

    def search(self, query: str) -> list[PluginEntry]:
        return self.list_plugins(search=query)

    def get_categories(self) -> dict[str, int]:
        categories: dict[str, int] = {}
        for plugin in self._plugins.values():
            categories[plugin.plugin_type] = categories.get(plugin.plugin_type, 0) + 1
        return categories

    def get_popular(self, limit: int = 10) -> list[PluginEntry]:
        return self.list_plugins(sort_by="downloads", limit=limit)

    def get_featured(self) -> list[PluginEntry]:
        return [p for p in self._plugins.values() if p.is_official]

    def update_stats(self, slug: str, downloads: int | None = None, rating: float | None = None) -> bool:
        entry = self._plugins.get(slug)
        if not entry:
            return False
        if downloads is not None:
            entry.downloads = downloads
        if rating is not None:
            entry.rating = rating
        return True


plugin_registry = PluginRegistry()


BUILTIN_PLUGINS = [
    PluginEntry(
        name="GitHub Integration",
        slug="github-integration",
        version="1.0.0",
        description="Connect with GitHub repositories, create issues, and manage PRs",
        author="SuperDev Team",
        plugin_type="integration",
        tags=["github", "git", "vcs"],
        downloads=1520,
        rating=4.8,
        is_official=True,
    ),
    PluginEntry(
        name="Slack Notifications",
        slug="slack-notifications",
        version="1.0.0",
        description="Send workflow and agent notifications to Slack channels",
        author="SuperDev Team",
        plugin_type="integration",
        tags=["slack", "notifications", "messaging"],
        downloads=980,
        rating=4.6,
        is_official=True,
    ),
    PluginEntry(
        name="Docker Runtime",
        slug="docker-runtime",
        version="1.0.0",
        description="Execute code in Docker containers for enhanced isolation",
        author="SuperDev Team",
        plugin_type="tool",
        tags=["docker", "runtime", "containers"],
        downloads=2100,
        rating=4.9,
        is_official=True,
    ),
    PluginEntry(
        name="Jira Integration",
        slug="jira-integration",
        version="1.0.0",
        description="Sync with Jira issues and sprint boards",
        author="Community",
        plugin_type="integration",
        tags=["jira", "project-management", "agile"],
        downloads=650,
        rating=4.3,
        is_official=False,
    ),
    PluginEntry(
        name="PostgreSQL Provider",
        slug="postgresql-provider",
        version="1.0.0",
        description="PostgreSQL database provider for knowledge base storage",
        author="SuperDev Team",
        plugin_type="provider",
        tags=["postgresql", "database", "storage"],
        downloads=1800,
        rating=4.7,
        is_official=True,
    ),
    PluginEntry(
        name="VS Code Extension",
        slug="vscode-extension",
        version="1.0.0",
        description="SuperDev integration for Visual Studio Code",
        author="SuperDev Team",
        plugin_type="ui",
        tags=["vscode", "editor", "ide"],
        downloads=3200,
        rating=4.8,
        is_official=True,
    ),
]

for plugin in BUILTIN_PLUGINS:
    plugin_registry.register(plugin)
