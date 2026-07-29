"""
Budget Optimizer - Optimizes advertising budget allocation
"""

from typing import Any, Dict, List
from uuid import UUID


class BudgetOptimizer:
    """Optimizes advertising budget"""

    def __init__(self, engine):
        self.engine = engine
        self.target_roas = engine.config.advertising.roas_target

    async def optimize(self, campaign_id: UUID, performance: Dict[str, Any]) -> Dict[str, Any]:
        current_roas = performance.get("roas", 0)
        current_spend = performance.get("spend", 0)

        if current_roas >= self.target_roas:
            return {
                "action": "increase",
                "recommended_budget": current_spend * 1.2,
                "reason": "ROAS above target, scale up",
            }
        elif current_roas > self.target_roas * 0.7:
            return {
                "action": "maintain",
                "recommended_budget": current_spend,
                "reason": "ROAS near target, optimize creatives",
            }
        else:
            return {
                "action": "decrease",
                "recommended_budget": current_spend * 0.7,
                "reason": "ROAS below target, reduce spend",
            }

    async def allocate_across_campaigns(
        self,
        campaigns: List[Dict],
        total_budget: float,
    ) -> Dict[str, float]:
        scored = []
        for c in campaigns:
            roas = c.get("roas", 0)
            score = max(0, roas)
            scored.append((score, c["id"]))

        total_score = sum(s for s, _ in scored)
        if total_score == 0:
            return {c["id"]: total_budget / len(campaigns) for c in campaigns}

        allocation = {}
        for score, cid in scored:
            allocation[cid] = (score / total_score) * total_budget

        return allocation

    async def forecast_spend(self, campaign_id: UUID, days: int = 7) -> Dict[str, Any]:
        return {"campaign_id": str(campaign_id), "forecasted_spend": 0.0, "confidence": 0.0}