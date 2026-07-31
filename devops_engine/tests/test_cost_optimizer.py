"""Tests for the cost optimizer subpackage (Volume 37, Fase 6)."""

from __future__ import annotations

import pytest

from devops_engine.cost_optimizer import CostEngine
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import Resource


@pytest.fixture()
def cost_engine() -> CostEngine:
    return CostEngine()


def _resource(name: str, cost_per_hour: float,
              utilization: float) -> Resource:
    return Resource(resource_id=f"r-{name}", name=name,
                    cost_per_hour=cost_per_hour,
                    metadata={"utilization": utilization})


class TestCostAnalyzer:
    def test_total_by_resource_avg(self, cost_engine: CostEngine) -> None:
        cost_engine.record_cost("db", 100.0)
        cost_engine.record_cost("db", 50.0)
        cost_engine.record_cost("cache", 30.0)
        analysis = cost_engine.analyze()
        assert analysis["total"] == 180.0
        assert analysis["by_resource"] == {"db": 150.0, "cache": 30.0}
        assert analysis["avg"] == 60.0


class TestSavingsCalculator:
    def test_rightsizing_saving(self, cost_engine: CostEngine) -> None:
        saving = cost_engine.recommendations.savings.rightsizing_saving(
            10.0, utilization=0.2)
        assert saving == 7.5

    def test_reserved_saving(self, cost_engine: CostEngine) -> None:
        saving = cost_engine.recommendations.savings.reserved_saving(
            100.0, discount=0.3)
        assert saving == 30.0


class TestRecommendationEngine:
    def test_downsize_low_utilization(self, cost_engine: CostEngine) -> None:
        recommendations = cost_engine.optimize(
            [_resource("db", 10.0, utilization=0.2)])
        assert len(recommendations) == 1
        assert recommendations[0].action == "downsize"
        assert recommendations[0].priority == "high"
        assert recommendations[0].estimated_saving == 7.5

    def test_reserved_medium_utilization(self, cost_engine: CostEngine) -> None:
        recommendations = cost_engine.optimize(
            [_resource("db", 10.0, utilization=0.4)])
        assert len(recommendations) == 1
        assert recommendations[0].action == "reserved_instances"

    def test_no_recommendation_healthy(self, cost_engine: CostEngine) -> None:
        recommendations = cost_engine.optimize(
            [_resource("db", 10.0, utilization=0.9)])
        assert recommendations == []


class TestCostEngine:
    def test_record_cost_event_and_metric(self, cost_engine: CostEngine) -> None:
        events = DevopsEvents()
        cost_engine.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.COST_RECORDED, seen.append)
        record = cost_engine.record_cost("db", 42.0)
        assert record.amount == 42.0
        assert len(seen) == 1
        assert cost_engine.metrics.count("devops.cost.records") == 1

    def test_optimize_events(self, cost_engine: CostEngine) -> None:
        events = DevopsEvents()
        cost_engine.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.COST_RECOMMENDATION, seen.append)
        recommendations = cost_engine.optimize(
            [_resource("db", 10.0, utilization=0.2)])
        assert len(recommendations) == 1
        assert len(seen) == 1
        assert cost_engine.metrics.count(
            "devops.cost.recommendations") == 1

    def test_analyze_passed_costs(self, cost_engine: CostEngine) -> None:
        records = [cost_engine.record_cost("db", 10.0),
                   cost_engine.record_cost("db", 20.0)]
        analysis = cost_engine.analyze(costs=records)
        assert analysis["total"] == 30.0

    def test_stats(self, cost_engine: CostEngine) -> None:
        cost_engine.record_cost("db", 10.0)
        cost_engine.record_cost("cache", 20.0)
        stats = cost_engine.stats()
        assert stats["records"] == 2
        assert stats["total"] == 30.0
