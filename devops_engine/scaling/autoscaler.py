"""Autoscaling decision logic (Volume 37, Fase 6)."""

from __future__ import annotations

from devops_engine.devops_models import AutoscalePolicy


class Autoscaler:
    """Computes target replica counts from utilization."""

    def decide(self, policy: AutoscalePolicy,
               current: int, utilization: float) -> int:
        if utilization > policy.cpu_threshold:
            return min(policy.max_replicas, current + 1)
        if utilization < policy.cpu_threshold * 0.5:
            return max(policy.min_replicas, current - 1)
        return current

    def apply(self, policy: AutoscalePolicy, current: int,
              target: int) -> bool:
        """True when the target differs from the current replica count."""
        return current != target
