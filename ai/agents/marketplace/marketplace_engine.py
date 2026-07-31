"""Marketplace engine for agent and skill marketplace."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .agent_publisher import AgentPublisher
from .agent_consumer import AgentConsumer
from .review_system import ReviewSystem
from .pricing_engine import PricingEngine


class MarketplaceEngine:
    """Central engine for the agent marketplace ecosystem."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._publisher = AgentPublisher()
        self._consumer = AgentConsumer()
        self._reviews = ReviewSystem()
        self._pricing = PricingEngine()
        self._listings: Dict[str, Dict[str, Any]] = {}

    def publish_agent(self, agent_spec: Dict[str, Any]) -> Dict[str, Any]:
        result = self._publisher.publish(agent_spec)
        if result.get("status") == "published":
            self._listings[result["agent_id"]] = agent_spec
        return result

    def search_agents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._consumer.search(query, self._listings)

    def install_agent(self, agent_id: str) -> Dict[str, Any]:
        return self._consumer.install(agent_id, self._listings)

    def add_review(self, agent_id: str, rating: float, text: str) -> Dict[str, Any]:
        return self._reviews.add_review(agent_id, rating, text)

    def get_reviews(self, agent_id: str) -> List[Dict[str, Any]]:
        return self._reviews.get_reviews(agent_id)

    def get_price(self, agent_id: str) -> Dict[str, Any]:
        return self._pricing.get_price(agent_id, self._listings)

    def list_all(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self._listings.items()]

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_listings": len(self._listings),
            "total_reviews": self._reviews.count(),
        }
