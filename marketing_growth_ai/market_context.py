"""
Market Context - Market data and context management
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from marketing_growth_ai.marketing_models import (
    MarketTrend,
    Competitor,
    MarketOpportunity,
)


class MarketContext:
    """Manages market data and context"""

    def __init__(self, engine):
        self.engine = engine
        self.config = engine.config
        self._market_data: Dict[str, Any] = {}
        self._competitors: Dict[UUID, Competitor] = {}
        self._trends: Dict[UUID, MarketTrend] = {}
        self._opportunities: Dict[UUID, MarketOpportunity] = {}

    async def initialize(self) -> None:
        await self._load_initial_data()

    async def shutdown(self) -> None:
        pass

    async def _load_initial_data(self) -> None:
        pass

    async def update_market_data(self, data: Dict[str, Any]) -> None:
        self._market_data.update(data)
        self._market_data["last_updated"] = datetime.utcnow().isoformat()

    def get_market_data(self) -> Dict[str, Any]:
        return self._market_data

    async def add_competitor(self, competitor: Competitor) -> UUID:
        self._competitors[competitor.id] = competitor
        return competitor.id

    async def get_competitor(self, competitor_id: UUID) -> Optional[Competitor]:
        return self._competitors.get(competitor_id)

    async def list_competitors(self) -> List[Competitor]:
        return list(self._competitors.values())

    async def add_trend(self, trend: MarketTrend) -> UUID:
        self._trends[trend.id] = trend
        return trend.id

    async def get_trend(self, trend_id: UUID) -> Optional[MarketTrend]:
        return self._trends.get(trend_id)

    async def list_trends(self, category: Optional[str] = None) -> List[MarketTrend]:
        trends = list(self._trends.values())
        if category:
            trends = [t for t in trends if t.category == category]
        return trends

    async def add_opportunity(self, opportunity: MarketOpportunity) -> UUID:
        self._opportunities[opportunity.id] = opportunity
        return opportunity.id

    async def get_opportunity(self, opportunity_id: UUID) -> Optional[MarketOpportunity]:
        return self._opportunities.get(opportunity_id)

    async def list_opportunities(self, min_confidence: float = 0.5) -> List[MarketOpportunity]:
        return [
            o for o in self._opportunities.values()
            if o.confidence >= min_confidence
        ]

    def get_status(self) -> Dict[str, Any]:
        return {
            "market_data_points": len(self._market_data),
            "competitors_tracked": len(self._competitors),
            "trends_detected": len(self._trends),
            "opportunities_identified": len(self._opportunities),
        }