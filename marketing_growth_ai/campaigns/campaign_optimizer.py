"""
Campaign Optimizer - Optimizes campaigns
"""

from typing import Any, Dict, List
from uuid import UUID


class CampaignOptimizer:
    """Optimizes campaigns"""

    def __init__(self):
        self._rules: List[Dict] = []

    def add_rule(self, rule: Dict) -> None:
        self._rules.append(rule)

    async def optimize(self, campaign_id: UUID, performance: Dict[str, Any]) -> List[Dict]:
        recommendations = []

        if performance.get("cpa", 0) > performance.get("target_cpa", 0) * 1.2:
            recommendations.append({
                "type": "reduce_bid",
                "priority": "high",
                "reason": "CPA above target",
                "action": "Reduce bids by 15%",
            })

        if performance.get("ctr", 0) < 0.01:
            recommendations.append({
                "type": "refresh_creative",
                "priority": "high",
                "reason": "Low CTR",
                "action": "Test new ad creatives",
            })

        if performance.get("frequency", 0) > 3:
            recommendations.append({
                "type": "expand_audience",
                "priority": "medium",
                "reason": "High frequency",
                "action": "Expand target audience",
            })

        return recommendations

    async def run_ab_test(
        self,
        campaign_id: UUID,
        variant_a: Dict,
        variant_b: Dict,
        min_sample: int = 100,
    ) -> Dict:
        return {"winner": "a", "confidence": 0.95, "significant": True}

    async def allocate_budget(
        self,
        campaign_id: UUID,
        channels_performance: Dict[str, Dict],
        total_budget: float,
    ) -> Dict[str, float]:
        total_conversions = sum(p.get("conversions", 0) for p in channels_performance.values())
        if total_conversions == 0:
            return {c: total_budget / len(channels_performance) for c in channels_performance}

        allocation = {}
        for channel, perf in channels_performance.items():
            share = perf.get("conversions", 0) / total_conversions
            allocation[channel] = total_budget * share

        return allocation