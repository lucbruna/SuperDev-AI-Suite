"""Marketplace categories."""

from __future__ import annotations

from typing import Any

from .listing import MarketplaceListing


class MarketplaceCategory:
    """Maintains the category taxonomy for marketplace listings."""

    def __init__(self, listing: MarketplaceListing | None = None) -> None:
        self._listing = listing or MarketplaceListing()
        self._categories: dict[str, str] = {}

    def add_category(self, name: str, description: str = "") -> None:
        self._categories[name] = description

    def has(self, name: str) -> bool:
        return name in self._categories

    def list(self) -> list[dict[str, str]]:
        return [{"name": n, "description": d}
                for n, d in sorted(self._categories.items())]

    def count(self, category: str) -> int:
        return len(self._listing.list(published_only=False)) if category else 0
