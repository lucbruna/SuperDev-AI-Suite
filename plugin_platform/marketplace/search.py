from __future__ import annotations

from typing import Any


class PluginSearch:
    def __init__(self, store: Any | None = None):
        if store is None:
            from .store import PluginStore
            store = PluginStore()
        self._store = store
        self._search_index: dict[str, set[str]] = {}

    def _tokenize(self, text: str) -> list[str]:
        import re
        tokens = re.findall(r"[a-zA-Z0-9_\-\.]+", text.lower())
        return tokens

    def build_index(self):
        self._search_index.clear()
        for plugin in self._store.list_all():
            text = f"{plugin.get('name', '')} {plugin.get('description', '')} {plugin.get('author', '')} {' '.join(plugin.get('tags', []))}"
            for token in self._tokenize(text):
                if token not in self._search_index:
                    self._search_index[token] = set()
                self._search_index[token].add(plugin.get("id", ""))

    def search(self, query: str, category: str = "", tag: str = "", sort: str = "relevance", limit: int = 20) -> list[dict[str, Any]]:
        tokens = self._tokenize(query)
        if not tokens:
            return self._store.search(category=category, tag=tag, sort=sort)[:limit]
        plugin_scores: dict[str, int] = {}
        for token in tokens:
            matches = self._search_index.get(token, set())
            for plugin_id in matches:
                plugin_scores[plugin_id] = plugin_scores.get(plugin_id, 0) + 1
        scored = sorted(plugin_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for plugin_id, score in scored:
            plugin = self._store.get(plugin_id)
            if plugin:
                if category and plugin.get("category") != category:
                    continue
                if tag and tag not in plugin.get("tags", []):
                    continue
                plugin["_score"] = score
                results.append(plugin)
                if len(results) >= limit:
                    break
        if sort == "downloads":
            results.sort(key=lambda p: p.get("downloads", 0), reverse=True)
        elif sort == "rating":
            results.sort(key=lambda p: p.get("rating", 0), reverse=True)
        return results

    def autocomplete(self, prefix: str, limit: int = 5) -> list[str]:
        prefix = prefix.lower()
        suggestions: list[str] = []
        for token in self._search_index:
            if token.startswith(prefix):
                suggestions.append(token)
            if len(suggestions) >= limit:
                break
        return sorted(suggestions)[:limit]

    def search_by_tag(self, tag: str) -> list[dict[str, Any]]:
        return self._store.search(tag=tag)

    def search_by_author(self, author: str) -> list[dict[str, Any]]:
        return self._store.search(query=author)

    def get_category_tree(self) -> dict[str, list[str]]:
        categories = self._store.get_categories()
        tree: dict[str, list[str]] = {}
        for cat in categories:
            cat_id = cat["id"]
            plugins = self._store.search(category=cat_id)
            tree[cat_id] = [p.get("id", "") for p in plugins[:10]]
        return tree

    def get_related(self, plugin_id: str, limit: int = 5) -> list[dict[str, Any]]:
        plugin = self._store.get(plugin_id)
        if not plugin:
            return []
        tags = plugin.get("tags", [])
        related: list[tuple[str, int]] = []
        for other in self._store.list_all():
            if other["id"] == plugin_id:
                continue
            overlap = len(set(tags) & set(other.get("tags", [])))
            if overlap > 0:
                related.append((other["id"], overlap))
        related.sort(key=lambda x: x[1], reverse=True)
        return [self._store.get(pid) for pid, _ in related[:limit] if self._store.get(pid)]