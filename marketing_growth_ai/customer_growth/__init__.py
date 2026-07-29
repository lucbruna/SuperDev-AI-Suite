"""
Customer Growth Package
"""

from marketing_growth_ai.customer_growth.growth_engine import GrowthEngine
from marketing_growth_ai.customer_growth.acquisition import AcquisitionManager
from marketing_growth_ai.customer_growth.retention import RetentionManager
from marketing_growth_ai.customer_growth.churn_prediction import ChurnPredictor

__all__ = [
    "GrowthEngine",
    "AcquisitionManager",
    "RetentionManager",
    "ChurnPredictor",
]