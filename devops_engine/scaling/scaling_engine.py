"""Scaling engine (Volume 37, Fase 6)."""

from __future__ import annotations

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import AutoscalePolicy
from devops_engine.scaling.autoscaler import Autoscaler
from devops_engine.scaling.metrics_provider import MetricsProvider
from devops_engine.scaling.policy_manager import PolicyManager


class ScalingEngine:
    """Facade over autoscaling policies and decisions."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.policies = PolicyManager()
        self.provider = MetricsProvider()
        self.autoscaler = Autoscaler()

    def create_policy(self, cluster_id: str, min_replicas: int = 1,
                      max_replicas: int = 10,
                      cpu_threshold: float = 0.75,
                      metric: str = "cpu") -> AutoscalePolicy:
        return self.policies.create(cluster_id, min_replicas,
                                    max_replicas, cpu_threshold, metric)

    def evaluate(self, policy_id: str,
                 utilization: float) -> dict[str, object]:
        policy = self.policies.get(policy_id)
        if policy is None:
            return {"applied": False, "current": 0, "target": 0,
                    "action": "unknown"}
        current = int(policy.metadata.get("current", 1))
        target = self.autoscaler.decide(policy, current, utilization)
        applied = self.autoscaler.apply(policy, current, target)
        policy.metadata["current"] = target
        action = "none"
        if applied and target > current:
            action = "up"
            self.events.publish(DevopsEventType.SCALED_UP,
                                {"policy_id": policy_id, "from": current,
                                 "to": target})
            self.metrics.increment("devops.scaling.up")
        elif applied and target < current:
            action = "down"
            self.events.publish(DevopsEventType.SCALED_DOWN,
                                {"policy_id": policy_id, "from": current,
                                 "to": target})
            self.metrics.increment("devops.scaling.down")
        return {"applied": applied, "current": current, "target": target,
                "action": action}

    def record(self, metric: str, value: float) -> None:
        self.provider.record(metric, value)

    def stats(self) -> dict[str, int | float]:
        return {
            "policies": self.policies.count(),
            "last_utilization": self.provider.last("cpu"),
        }
