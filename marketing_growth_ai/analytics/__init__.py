"""
Analytics Package
"""

from marketing_growth_ai.analytics.marketing_analytics import MarketingAnalytics
from marketing_growth_ai.analytics.attribution import AttributionModel
from marketing_growth_ai.analytics.conversion_analysis import ConversionAnalyzer
from marketing_growth_ai.analytics.funnel_analysis import FunnelAnalyzer

__all__ = [
    "MarketingAnalytics",
    "AttributionModel",
    "ConversionAnalyzer",
    "FunnelAnalyzer",
]