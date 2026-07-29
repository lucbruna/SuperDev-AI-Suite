"""
Attribution Model - Attribution analysis
"""

from typing import Any, Dict
from uuid import UUID


class AttributionModel:
    """Attribution analysis"""

    def __init__(self, analytics):
        self.analytics = analytics

    async def calculate(self, campaign_id: UUID, model: str = "data_driven") -> Dict[str, Any]:
        return {"model": model, "attribution": {}, "confidence": 0.9}

    async def compare_models(self, campaign_id: UUID) -> Dict[str, Any]:
        return {"models": ["first_touch", "last_touch", "linear", "data_driven"]}