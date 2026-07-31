"""Marketplace discovery and search."""

from __future__ import annotations

from typing import Any


class MarketplaceDiscovery:
    """Searches and filters marketplace listings."""

    def __init__(self, listings: dict[str, dict[str, Any]]) -> None:
        self._listings = listings

    def search(self, query: str = "", category: str | None = None,
               tag: str | None = None) -> list[dict[str, Any]]:
        query = query.lower().strip()
        results: list[dict[str, Any]] = []
        for listing in self._listings.values():
            if not listing["published"]:
                continue
            if category and listing["category"] != category:
                continue
            if tag and tag not in listing["tags"]:
                continue
            if query and query not in listing["name"].lower() \
                    and query not in listing["description"].lower():
                continue
            results.append(listing)
        return sorted(results, key=lambda l: l["installs"], reverse=True)

    def by_category(self, category: str) -> list[dict[str, Any]]:
        return self.search(category=category)

    def popular(self, limit: int = 10) -> list[dict[str, Any]]:
        listings = [l for l in self._listings.values() if l["published"]]
        listings.sort(key=lambda l: l["installs"], reverse=True)
        return listings[:limit]
