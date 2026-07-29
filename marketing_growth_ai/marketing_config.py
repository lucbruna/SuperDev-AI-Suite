"""
Configuration for Marketing Growth AI
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MarketIntelligenceConfig:
    competitor_tracking_enabled: bool = True
    trend_detection_interval: int = 3600
    forecast_horizon_days: int = 90
    data_sources: List[str] = field(default_factory=lambda: ["google_trends", "social_media", "news", "industry_reports"])
    min_trend_confidence: float = 0.7


@dataclass
class CampaignConfig:
    auto_optimization: bool = True
    ab_test_enabled: bool = True
    min_sample_size: int = 100
    confidence_threshold: float = 0.95
    max_budget_per_campaign: float = 100000
    channels: List[str] = field(default_factory=lambda: ["google", "facebook", "instagram", "linkedin", "email"])


@dataclass
class AdvertisingConfig:
    budget_optimizer_enabled: bool = True
    roas_target: float = 3.0
    cpa_target: float = 50.0
    bid_strategy: str = "target_roas"
    daily_budget_cap: float = 10000


@dataclass
class ContentConfig:
    brand_voice: str = "professional"
    languages: List[str] = field(default_factory=lambda: ["pt-BR", "en"])
    content_types: List[str] = field(default_factory=lambda: ["blog", "social", "email", "ad_copy", "landing_page"])
    seo_optimization: bool = True


@dataclass
class SEOConfig:
    target_keywords: int = 100
    competitor_analysis: bool = True
    ranking_check_interval: int = 86400
    content_gap_analysis: bool = True


@dataclass
class SocialConfig:
    platforms: List[str] = field(default_factory=lambda: ["instagram", "facebook", "linkedin", "twitter", "tiktok"])
    monitoring_enabled: bool = True
    sentiment_analysis: bool = True
    engagement_tracking: bool = True
    community_management: bool = False


@dataclass
class AnalyticsConfig:
    attribution_model: str = "data_driven"
    funnel_tracking: bool = True
    cohort_analysis: bool = True
    real_time_dashboard: bool = True


@dataclass
class CustomerGrowthConfig:
    churn_prediction_enabled: bool = True
    ltv_prediction: bool = True
    segmentation_enabled: bool = True
    retention_campaigns: bool = True
    acquisition_optimization: bool = True


@dataclass
class MarketingConfig:
    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///marketing_growth.db"
    redis_url: str = "redis://localhost:6379/2"
    api_keys: Dict[str, str] = field(default_factory=dict)

    market_intelligence: MarketIntelligenceConfig = field(default_factory=MarketIntelligenceConfig)
    campaigns: CampaignConfig = field(default_factory=CampaignConfig)
    advertising: AdvertisingConfig = field(default_factory=AdvertisingConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    seo: SEOConfig = field(default_factory=SEOConfig)
    social: SocialConfig = field(default_factory=SocialConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    customer_growth: CustomerGrowthConfig = field(default_factory=CustomerGrowthConfig)

    @classmethod
    def from_env(cls) -> "MarketingConfig":
        config = cls()
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.database_url = os.getenv("DATABASE_URL", config.database_url)
        config.redis_url = os.getenv("REDIS_URL", config.redis_url)

        config.api_keys = {
            "google_ads": os.getenv("GOOGLE_ADS_API_KEY", ""),
            "facebook_ads": os.getenv("FACEBOOK_ADS_API_KEY", ""),
            "google_analytics": os.getenv("GA_API_KEY", ""),
            "semrush": os.getenv("SEMRUSH_API_KEY", ""),
            "ahrefs": os.getenv("AHREFS_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", ""),
        }
        return config