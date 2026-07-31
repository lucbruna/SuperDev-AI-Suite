"""Pricing engine for marketplace agents."""
from __future__ import annotations

from typing import Any, Dict


class PricingEngine:
    """Determines pricing for marketplace agents."""

    def __init__(self) -> None:
        self._base_prices: Dict[str, float] = {
            "free": 0.0,
            "basic": 9.99,
            "pro": 29.99,
            "enterprise": 99.99,
        }
        self._default_tier = "basic"

    def get_price(self, agent_id: str,
                  listings: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        listing = listings.get(agent_id, {})
        tier = listing.get("tier", self._default_tier)
        price = self._base_prices.get(tier, self._base_prices[self._default_tier])
        return {
            "agent_id": agent_id,
            "tier": tier,
            "price": price,
            "currency": "USD",
        }

    def set_tier(self, agent_id: str, tier: str) -> bool:
        if tier in self._base_prices:
            return True
        return False

    def get_tiers(self) -> Dict[str, float]:
        return dict(self._base_prices)
