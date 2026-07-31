"""Marketplace engine: facade over listings, discovery, install, and reviews."""

from __future__ import annotations

import logging
from typing import Any

from .category import MarketplaceCategory
from .discovery import MarketplaceDiscovery
from .install import MarketplaceInstaller
from .listing import MarketplaceListing
from .review import MarketplaceReview


class MarketplaceEngine:
    """Facade for the marketplace subsystem."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.marketplace")
        self.listing = MarketplaceListing()
        self.discovery = MarketplaceDiscovery(self.listing._listings)
        self.installer = MarketplaceInstaller(self.listing)
        self.reviews = MarketplaceReview(self.listing)
        self.categories = MarketplaceCategory(self.listing)

    def publish(self, listing_id: str, name: str, category: str,
                description: str = "", tags: list[str] | None = None) -> None:
        self.listing.publish(listing_id, name, category, description, tags=tags)

    def search(self, query: str = "", category: str | None = None,
               tag: str | None = None) -> list[dict[str, Any]]:
        return self.discovery.search(query, category, tag)

    def install(self, listing_id: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.installer.install(listing_id, config)

    def rate(self, listing_id: str, author: str, rating: int,
             comment: str = "") -> None:
        self.reviews.add_review(listing_id, author, rating, comment)

    def stats(self) -> dict[str, int]:
        return {
            "listings": len(self.listing.list()),
            "installed": len(self.installer.list_installed()),
            "categories": len(self.categories.list()),
        }
