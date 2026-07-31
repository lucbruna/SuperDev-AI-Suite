"""Marketplace reviews and ratings."""

from __future__ import annotations

import time
from typing import Any

from .listing import MarketplaceListing


class MarketplaceReview:
    """Collects reviews and computes average ratings."""

    def __init__(self, listing: MarketplaceListing) -> None:
        self._listing = listing
        self._reviews: dict[str, list[dict[str, Any]]] = {}

    def add_review(self, listing_id: str, author: str,
                   rating: int, comment: str = "") -> None:
        rating = max(1, min(5, rating))
        self._reviews.setdefault(listing_id, []).append({
            "author": author,
            "rating": rating,
            "comment": comment,
            "timestamp": time.time(),
        })
        self._listing.set_rating(listing_id, self.average(listing_id))

    def average(self, listing_id: str) -> float:
        reviews = self._reviews.get(listing_id, [])
        if not reviews:
            return 0.0
        return round(sum(r["rating"] for r in reviews) / len(reviews), 2)

    def count(self, listing_id: str) -> int:
        return len(self._reviews.get(listing_id, []))

    def list(self, listing_id: str) -> list[dict[str, Any]]:
        return list(self._reviews.get(listing_id, []))
