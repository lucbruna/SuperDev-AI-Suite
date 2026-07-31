"""Marketplace listing management."""

from __future__ import annotations

from typing import Any


class MarketplaceListing:
    """Registers and manages connector listings in the marketplace."""

    def __init__(self) -> None:
        self._listings: dict[str, dict[str, Any]] = {}

    def publish(self, listing_id: str, name: str, category: str,
                description: str = "", version: str = "1.0.0",
                tags: list[str] | None = None) -> None:
        self._listings[listing_id] = {
            "listing_id": listing_id,
            "name": name,
            "category": category,
            "description": description,
            "version": version,
            "tags": tags or [],
            "installs": 0,
            "rating": 0.0,
            "published": True,
        }

    def get(self, listing_id: str) -> dict[str, Any]:
        if listing_id not in self._listings:
            raise KeyError(listing_id)
        return self._listings[listing_id]

    def unpublish(self, listing_id: str) -> bool:
        if listing_id not in self._listings:
            return False
        self._listings[listing_id]["published"] = False
        return True

    def increment_installs(self, listing_id: str) -> None:
        if listing_id in self._listings:
            self._listings[listing_id]["installs"] += 1

    def set_rating(self, listing_id: str, rating: float) -> None:
        if listing_id in self._listings:
            self._listings[listing_id]["rating"] = rating

    def list(self, published_only: bool = True) -> list[dict[str, Any]]:
        listings = self._listings.values()
        if published_only:
            listings = [l for l in listings if l["published"]]
        return sorted(listings, key=lambda l: l["name"])
