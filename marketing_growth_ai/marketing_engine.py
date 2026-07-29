"""
Marketing Engine - Core marketing orchestration
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from marketing_growth_ai.marketing_config import MarketingConfig
from marketing_growth_ai.marketing_models import (
    Campaign,
    CampaignStatus,
    CampaignType,
    Channel,
    CustomerSegment,
    MarketTrend,
    AdvertisingMetrics,
    ContentPiece,
    SEOKeyword,
    SocialPost,
    GrowthMetrics,
)
from marketing_growth_ai.market_intelligence.market_engine import MarketEngine
from marketing_growth_ai.campaigns.campaign_engine import CampaignEngine
from marketing_growth_ai.advertising.advertising_engine import AdvertisingEngine
from marketing_growth_ai.content.content_engine import ContentEngine
from marketing_growth_ai.seo.seo_engine import SEOEngine
from marketing_growth_ai.social.social_engine import SocialEngine
from marketing_growth_ai.analytics.marketing_analytics import MarketingAnalytics
from marketing_growth_ai.customer_growth.growth_engine import GrowthEngine


class MarketingEngine:
    """Core marketing orchestration engine"""

    def __init__(self, config: Optional[MarketingConfig] = None):
        self.config = config or MarketingConfig.from_env()
        self.id = uuid4()
        self.created_at = datetime.utcnow()

        self.market_engine = MarketEngine(self)
        self.campaign_engine = CampaignEngine(self)
        self.advertising_engine = AdvertisingEngine(self)
        self.content_engine = ContentEngine(self)
        self.seo_engine = SEOEngine(self)
        self.social_engine = SocialEngine(self)
        self.analytics = MarketingAnalytics(self)
        self.growth_engine = GrowthEngine(self)

        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        await self.market_engine.initialize()
        await self.campaign_engine.initialize()
        await self.advertising_engine.initialize()
        await self.content_engine.initialize()
        await self.seo_engine.initialize()
        await self.social_engine.initialize()
        await self.analytics.initialize()
        await self.growth_engine.initialize()

        self._initialized = True

    async def shutdown(self) -> None:
        await self.market_engine.shutdown()
        await self.campaign_engine.shutdown()
        await self.advertising_engine.shutdown()
        await self.content_engine.shutdown()
        await self.seo_engine.shutdown()
        await self.social_engine.shutdown()
        await self.analytics.shutdown()
        await self.growth_engine.shutdown()

    async def analyze_growth_opportunity(
        self,
        objective: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze growth opportunity and provide strategy"""

        market_analysis = await self.market_engine.analyze_market(context)
        trend_analysis = await self.market_engine.detect_trends(context)
        competitor_analysis = await self.market_engine.analyze_competitors(context)

        customer_insights = await self.growth_engine.analyze_customers(context)
        campaign_performance = await self.analytics.analyze_performance(context)

        strategy = await self._generate_strategy(
            objective=objective,
            market=market_analysis,
            trends=trend_analysis,
            competitors=competitor_analysis,
            customers=customer_insights,
            performance=campaign_performance,
        )

        return {
            "objective": objective,
            "market_analysis": market_analysis,
            "trend_analysis": trend_analysis,
            "competitor_analysis": competitor_analysis,
            "customer_insights": customer_insights,
            "campaign_performance": campaign_performance,
            "strategy": strategy,
            "recommendations": strategy.get("recommendations", []),
            "projected_impact": strategy.get("projected_impact", {}),
        }

    async def _generate_strategy(
        self,
        objective: str,
        market: Dict,
        trends: List,
        competitors: Dict,
        customers: Dict,
        performance: Dict,
    ) -> Dict[str, Any]:
        recommendations = []

        if trends:
            recommendations.append({
                "type": "trend_capitalization",
                "priority": "high",
                "description": f"Capitalize on {len(trends)} emerging trends",
                "actions": [f"Create content for {t.get('name', 'trend')}" for t in trends[:3]],
            })

        if competitors.get("gaps"):
            recommendations.append({
                "type": "competitive_gap",
                "priority": "high",
                "description": f"Fill {len(competitors['gaps'])} competitive gaps",
                "actions": [f"Launch {g['opportunity']}" for g in competitors['gaps'][:3]],
            })

        if customers.get("churn_risk_segments"):
            recommendations.append({
                "type": "retention",
                "priority": "critical",
                "description": f"Retain {len(customers['churn_risk_segments'])} at-risk segments",
                "actions": [f"Campaign for {s['name']}" for s in customers['churn_risk_segments'][:2]],
            })

        if performance.get("top_channels"):
            recommendations.append({
                "type": "channel_optimization",
                "priority": "medium",
                "description": f"Scale top performing channels: {', '.join(performance['top_channels'][:3])}",
                "actions": [f"Increase budget for {c}" for c in performance['top_channels'][:2]],
            })

        return {
            "recommendations": recommendations,
            "projected_impact": {
                "revenue_increase_pct": 15 + len(recommendations) * 5,
                "customer_acquisition_improvement": 20,
                "retention_improvement": 15,
            },
            "timeline": "90 days",
            "budget_required": sum(len(r.get("actions", [])) * 5000 for r in recommendations),
        }

    async def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        objective: str,
        target_audience: Dict,
        budget: float,
        channels: List[Channel],
        duration_days: int = 30,
    ) -> Campaign:
        """Create and launch a campaign"""
        return await self.campaign_engine.create_campaign(
            name=name,
            campaign_type=campaign_type,
            objective=objective,
            target_audience=target_audience,
            budget=budget,
            channels=channels,
            duration_days=duration_days,
        )

    async def optimize_advertising(
        self,
        campaign_id: UUID,
        target_roas: float = 3.0,
    ) -> AdvertisingMetrics:
        """Optimize advertising spend"""
        return await self.advertising_engine.optimize_campaign(campaign_id, target_roas)

    async def generate_content(
        self,
        content_type: str,
        topic: str,
        target_audience: Dict,
        brand_voice: str = "professional",
    ) -> ContentPiece:
        """Generate marketing content"""
        return await self.content_engine.generate(
            content_type=content_type,
            topic=topic,
            target_audience=target_audience,
            brand_voice=brand_voice,
        )

    async def analyze_seo(
        self,
        domain: str,
        keywords: List[str] = None,
    ) -> Dict[str, Any]:
        """Analyze SEO performance"""
        return await self.seo_engine.analyze(domain, keywords)

    async def monitor_social(
        self,
        brand_keywords: List[str],
        competitors: List[str] = None,
    ) -> Dict[str, Any]:
        """Monitor social media"""
        return await self.social_engine.monitor(brand_keywords, competitors)

    async def get_growth_metrics(self, period_days: int = 30) -> GrowthMetrics:
        """Get growth metrics"""
        return await self.growth_engine.get_metrics(period_days)

    def get_status(self) -> Dict[str, Any]:
        return {
            "engine_id": str(self.id),
            "initialized": self._initialized,
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
            "components": {
                "market_intelligence": self.market_engine.get_status(),
                "campaigns": self.campaign_engine.get_status(),
                "advertising": self.advertising_engine.get_status(),
                "content": self.content_engine.get_status(),
                "seo": self.seo_engine.get_status(),
                "social": self.social_engine.get_status(),
                "analytics": self.analytics.get_status(),
                "growth": self.growth_engine.get_status(),
            },
        }