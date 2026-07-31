"""Cost analysis (Volume 37, Fase 6)."""

from __future__ import annotations

from devops_engine.devops_models import CostRecord


class CostAnalyzer:
    """Aggregates cost records."""

    def total(self, costs: list[CostRecord]) -> float:
        return round(sum(cost.amount for cost in costs), 2)

    def by_resource(self, costs: list[CostRecord]) -> dict[str, float]:
        grouped: dict[str, float] = {}
        for cost in costs:
            grouped[cost.resource] = round(
                grouped.get(cost.resource, 0.0) + cost.amount, 2)
        return grouped

    def avg(self, costs: list[CostRecord]) -> float:
        if not costs:
            return 0.0
        return round(self.total(costs) / len(costs), 2)
