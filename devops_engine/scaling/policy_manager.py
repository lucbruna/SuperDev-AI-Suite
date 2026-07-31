"""Autoscaling policy management (Volume 37, Fase 6)."""

from __future__ import annotations

from devops_engine.devops_models import AutoscalePolicy
from devops_engine.devops_protocols import new_id, now


class PolicyManager:
    """Creates and manages autoscaling policies."""

    def __init__(self) -> None:
        self._policies: dict[str, AutoscalePolicy] = {}

    def create(self, cluster_id: str, min_replicas: int = 1,
               max_replicas: int = 10,
               cpu_threshold: float = 0.75,
               metric: str = "cpu") -> AutoscalePolicy:
        policy = AutoscalePolicy(
            policy_id=new_id("policy"),
            cluster_id=cluster_id,
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            cpu_threshold=float(cpu_threshold),
            metric=metric,
            created_at=now(),
        )
        self._policies[policy.policy_id] = policy
        return policy

    def get(self, policy_id: str) -> AutoscalePolicy | None:
        return self._policies.get(policy_id)

    def list(self) -> list[AutoscalePolicy]:
        return list(self._policies.values())

    def count(self) -> int:
        return len(self._policies)

    def remove(self, policy_id: str) -> bool:
        return self._policies.pop(policy_id, None) is not None
