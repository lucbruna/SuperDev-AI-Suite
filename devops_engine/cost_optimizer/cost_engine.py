"""Cost optimization engine (Volume 37, Fase 6)."""

from __future__ import annotations

from devops_engine.cost_optimizer.cost_analyzer import CostAnalyzer
from devops_engine.cost_optimizer.recommendation_engine import \
    RecommendationEngine
from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (CostRecommendation, CostRecord,
                                         Resource)
from devops_engine.devops_protocols import new_id, now


class CostEngine:
    """Facade over cost records, analysis and recommendations."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self._costs: list[CostRecord] = []
        self.analyzer = CostAnalyzer()
        self.recommendations = RecommendationEngine()

    def record_cost(self, resource: str, amount: float,
                    period: str = "") -> CostRecord:
        record = CostRecord(
            cost_id=new_id("cost"),
            provider=self.config.provider,
            region=self.config.region,
            resource=resource,
            amount=round(float(amount), 2),
            period=period,
            created_at=now(),
        )
        self._costs.append(record)
        self.events.publish(DevopsEventType.COST_RECORDED,
                            {"cost_id": record.cost_id,
                             "resource": resource})
        self.metrics.increment("devops.cost.records")
        return record

    def optimize(self, resources: list[Resource],
                 costs: list[CostRecord] | None = None
                 ) -> list[CostRecommendation]:
        recommendations = self.recommendations.recommend(resources, costs)
        for item in recommendations:
            self.events.publish(DevopsEventType.COST_RECOMMENDATION,
                                {"resource": item.resource,
                                 "action": item.action})
            self.metrics.increment("devops.cost.recommendations")
        return recommendations

    def analyze(self, costs: list[CostRecord] | None = None) -> dict:
        source = costs if costs is not None else self._costs
        return {
            "total": self.analyzer.total(source),
            "by_resource": self.analyzer.by_resource(source),
            "avg": self.analyzer.avg(source),
        }

    def stats(self) -> dict[str, int | float]:
        return {
            "records": len(self._costs),
            "total": self.analyzer.total(self._costs),
        }
