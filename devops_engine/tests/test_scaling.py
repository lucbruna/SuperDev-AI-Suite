"""Tests for the scaling subpackage (Volume 37, Fase 6)."""

from __future__ import annotations

import pytest

from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.scaling import ScalingEngine


@pytest.fixture()
def scaling() -> ScalingEngine:
    return ScalingEngine()


class TestPolicyManager:
    def test_create_defaults(self, scaling: ScalingEngine) -> None:
        policy = scaling.create_policy("c1")
        assert policy.min_replicas == 1
        assert policy.max_replicas == 10
        assert policy.cpu_threshold == 0.75
        assert scaling.policies.count() == 1

    def test_remove(self, scaling: ScalingEngine) -> None:
        policy = scaling.create_policy("c1")
        assert scaling.policies.remove(policy.policy_id) is True
        assert scaling.policies.count() == 0


class TestAutoscaler:
    def test_scale_up(self, scaling: ScalingEngine) -> None:
        policy = scaling.create_policy("c1")
        assert scaling.autoscaler.decide(policy, current=2,
                                         utilization=0.95) == 3

    def test_scale_down(self, scaling: ScalingEngine) -> None:
        policy = scaling.create_policy("c1")
        assert scaling.autoscaler.decide(policy, current=4,
                                         utilization=0.1) == 3

    def test_hold(self, scaling: ScalingEngine) -> None:
        policy = scaling.create_policy("c1")
        assert scaling.autoscaler.decide(policy, current=3,
                                         utilization=0.5) == 3

    def test_bounded_by_max(self, scaling: ScalingEngine) -> None:
        policy = scaling.create_policy("c1", max_replicas=3)
        assert scaling.autoscaler.decide(policy, current=3,
                                         utilization=0.99) == 3

    def test_bounded_by_min(self, scaling: ScalingEngine) -> None:
        policy = scaling.create_policy("c1", min_replicas=2)
        assert scaling.autoscaler.decide(policy, current=2,
                                         utilization=0.0) == 2


class TestScalingEngine:
    def test_evaluate_up(self, scaling: ScalingEngine) -> None:
        events = DevopsEvents()
        scaling.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.SCALED_UP, seen.append)
        policy = scaling.create_policy("c1")
        result = scaling.evaluate(policy.policy_id, utilization=0.95)
        assert result["action"] == "up"
        assert result["target"] == 2
        assert len(seen) == 1
        assert scaling.metrics.count("devops.scaling.up") == 1

    def test_evaluate_down(self, scaling: ScalingEngine) -> None:
        events = DevopsEvents()
        scaling.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.SCALED_DOWN, seen.append)
        policy = scaling.create_policy("c1", min_replicas=1)
        scaling.evaluate(policy.policy_id, utilization=0.95)
        result = scaling.evaluate(policy.policy_id, utilization=0.05)
        assert result["action"] == "down"
        assert len(seen) == 1
        assert scaling.metrics.count("devops.scaling.down") == 1

    def test_evaluate_hold(self, scaling: ScalingEngine) -> None:
        events = DevopsEvents()
        scaling.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.SCALED_UP, seen.append)
        policy = scaling.create_policy("c1")
        result = scaling.evaluate(policy.policy_id, utilization=0.5)
        assert result["action"] == "none"
        assert result["applied"] is False
        assert len(seen) == 0

    def test_evaluate_missing_policy(self, scaling: ScalingEngine) -> None:
        result = scaling.evaluate("nope", utilization=0.9)
        assert result["applied"] is False
        assert result["action"] == "unknown"

    def test_metrics_provider(self, scaling: ScalingEngine) -> None:
        scaling.record("cpu", 0.4)
        scaling.record("cpu", 0.6)
        assert scaling.provider.avg("cpu") == 0.5
        assert scaling.provider.last("cpu") == 0.6

    def test_stats(self, scaling: ScalingEngine) -> None:
        scaling.create_policy("c1")
        scaling.record("cpu", 0.8)
        stats = scaling.stats()
        assert stats["policies"] == 1
        assert stats["last_utilization"] == 0.8
