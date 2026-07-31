"""Cost recommendation engine (Volume 37, Fase 6)."""

from __future__ import annotations

from devops_engine.cost_optimizer.savings_calculator import \
    SavingsCalculator
from devops_engine.devops_models import CostRecommendation, Resource
from devops_engine.devops_protocols import new_id, now


class RecommendationEngine:
    """Builds cost recommendations from resource utilization."""

    def __init__(self) -> None:
        self.savings = SavingsCalculator()

    def recommend(self, resources: list[Resource],
                  costs=None) -> list[CostRecommendation]:
        recommendations: list[CostRecommendation] = []
        for resource in resources:
            utilization = float(resource.metadata.get("utilization", 0.5))
            if utilization < 0.3:
                saving = self.savings.rightsizing_saving(
                    resource.cost_per_hour, utilization)
                recommendations.append(CostRecommendation(
                    recommendation_id=new_id("recommendation"),
                    resource=resource.name,
                    action="downsize",
                    estimated_saving=saving,
                    priority="high",
                    created_at=now()))
            elif utilization < 0.6:
                saving = self.savings.reserved_saving(
                    resource.cost_per_hour)
                recommendations.append(CostRecommendation(
                    recommendation_id=new_id("recommendation"),
                    resource=resource.name,
                    action="reserved_instances",
                    estimated_saving=saving,
                    priority="medium",
                    created_at=now()))
        return recommendations
