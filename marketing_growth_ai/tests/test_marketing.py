"""
Tests for Marketing Growth AI
"""

import pytest
import asyncio
from uuid import UUID

from marketing_growth_ai.marketing_config import MarketingConfig
from marketing_growth_ai.marketing_models import (
    Campaign,
    CampaignStatus,
    CampaignType,
    Channel,
    CustomerSegment,
    MarketTrend,
    TrendDirection,
    ContentType,
)
from marketing_growth_ai.marketing_engine import MarketingEngine


@pytest.fixture
def config():
    return MarketingConfig.from_env()


@pytest.fixture
def engine(config):
    return MarketingEngine(config)


@pytest.mark.asyncio
async def test_engine_initialization(engine):
    await engine.initialize()
    assert engine._initialized is True
    await engine.shutdown()


@pytest.mark.asyncio
async def test_growth_opportunity_analysis(engine):
    await engine.initialize()

    result = await engine.analyze_growth_opportunity(
        objective="Increase revenue by 20%",
        context={"industry": "saas", "geography": "US"},
    )

    assert result is not None
    assert "strategy" in result
    assert "recommendations" in result
    assert "projected_impact" in result

    await engine.shutdown()


@pytest.mark.asyncio
async def test_campaign_creation(engine):
    await engine.initialize()

    campaign = await engine.create_campaign(
        name="Test Campaign",
        campaign_type=CampaignType.ACQUISITION,
        objective="Test",
        target_audience={"segment": "tech"},
        budget=10000,
        channels=[Channel.GOOGLE_SEARCH, Channel.FACEBOOK],
    )

    assert campaign is not None
    assert campaign.name == "Test Campaign"
    assert campaign.budget == 10000
    assert Channel.GOOGLE_SEARCH in campaign.channels

    await engine.shutdown()


@pytest.mark.asyncio
async def test_content_generation(engine):
    await engine.initialize()

    content = await engine.generate_content(
        content_type="blog_post",
        topic="AI in Marketing",
        target_audience={"segment": "marketers"},
        brand_voice="professional",
    )

    assert content is not None
    assert "AI in Marketing" in content.body

    await engine.shutdown()


@pytest.mark.asyncio
async def test_seo_analysis(engine):
    await engine.initialize()

    result = await engine.analyze_seo(domain="example.com", keywords=["ai", "marketing"])

    assert result is not None
    assert "domain" in result

    await engine.shutdown()


@pytest.mark.asyncio
async def test_social_monitoring(engine):
    await engine.initialize()

    result = await engine.monitor_social(brand_keywords=["brand"], competitors=["competitor"])

    assert result is not None
    assert "brand_mentions" in result

    await engine.shutdown()


@pytest.mark.asyncio
async def test_growth_metrics(engine):
    await engine.initialize()

    metrics = await engine.get_growth_metrics(period_days=30)

    assert metrics is not None

    await engine.shutdown()


@pytest.mark.asyncio
async def test_engine_status(engine):
    await engine.initialize()

    status = engine.get_status()

    assert status is not None
    assert "engine_id" in status
    assert "components" in status

    await engine.shutdown()


@pytest.mark.asyncio
async def test_market_engine(engine):
    await engine.initialize()

    result = await engine.market_engine.analyze_market("saas", "US")
    assert result is not None
    assert "industry" in result

    await engine.shutdown()


@pytest.mark.asyncio
async def test_campaign_engine(engine):
    await engine.initialize()

    from datetime import datetime
    campaign = await engine.campaign_engine.create_campaign(
        name="Test",
        campaign_type=CampaignType.AWARENESS,
        objective="Brand awareness",
        target_audience={"age": "25-35"},
        channels=[Channel.INSTAGRAM],
        budget=5000,
        start_date=datetime.utcnow(),
    )

    assert campaign is not None
    await engine.shutdown()


@pytest.mark.asyncio
async def test_advertising_engine(engine):
    await engine.initialize()

    campaign_id = await engine.advertising_engine.create_ad_campaign(
        name="Ad Test",
        channel=Channel.GOOGLE_SEARCH,
        budget=1000,
        targeting={"keywords": ["test"]},
        creative={"headline": "Test"},
    )

    assert campaign_id is not None
    await engine.shutdown()


@pytest.mark.asyncio
async def test_content_engine(engine):
    await engine.initialize()

    content = await engine.content_engine.generate(
        content_type="social_post",
        topic="Test Topic",
        target_audience={"segment": "general"},
    )

    assert content is not None
    await engine.shutdown()


@pytest.mark.asyncio
async def test_growth_engine(engine):
    await engine.initialize()

    segments = await engine.growth_engine.identify_segments()
    assert isinstance(segments, list)

    await engine.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])