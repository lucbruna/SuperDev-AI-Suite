from __future__ import annotations

from typing import Any

from ..data_models import DataClassification, DataRecord, GovernancePolicy, RetentionPolicy


class GovernanceEngine:
    """Data governance — ownership, policies, compliance, privacy, retention, classification."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.governance
        self._policies: dict[str, GovernancePolicy] = {}
        self._ownership: dict[str, str] = {}
        self._retention: dict[str, int] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- policies ------------------------------------------------------------

    def create_policy(
        self,
        name: str,
        rules: list[dict[str, Any]] | None = None,
        scope: str = "",
    ) -> GovernancePolicy:
        policy = GovernancePolicy(name=name, rules=rules or [], scope=scope)
        self._policies[policy.policy_id] = policy
        self.engine.registry.register_policy(policy)
        return policy

    def get_policy(self, policy_id: str) -> GovernancePolicy | None:
        return self._policies.get(policy_id)

    def list_policies(self) -> list[GovernancePolicy]:
        return list(self._policies.values())

    async def evaluate_policy(self, policy_id: str, context: dict[str, Any]) -> bool:
        policy = self._policies.get(policy_id)
        if not policy or not policy.enabled:
            return True
        for rule in policy.rules:
            field = rule.get("field")
            allowed = rule.get("allowed", [])
            if field in context and context[field] not in allowed:
                return False
        return True

    # -- ownership -----------------------------------------------------------

    def assign_owner(self, asset_id: str, owner: str) -> None:
        self._ownership[asset_id] = owner
        self.engine.metrics.increment("governance.assets_assigned")

    def get_owner(self, asset_id: str) -> str:
        return self._ownership.get(asset_id, "")

    # -- classification ------------------------------------------------------

    def classify_record(
        self,
        record: DataRecord,
        default: DataClassification = DataClassification.INTERNAL,
    ) -> DataClassification:
        return self.engine.security.classify(record, default)

    # -- retention -----------------------------------------------------------

    def set_retention(self, asset_id: str, days: int) -> None:
        self._retention[asset_id] = days

    def retention_days_for(self, asset_id: str) -> int:
        return self._retention.get(asset_id, self.config.default_retention_days)

    # -- compliance ----------------------------------------------------------

    def compliance_summary(self) -> dict[str, Any]:
        return {
            "policies": len(self._policies),
            "owned_assets": len(self._ownership),
            "retention_rules": len(self._retention),
            "privacy_enabled": self.config.privacy_enabled,
            "retention_enabled": self.config.retention_enabled,
            "compliance_enabled": self.config.compliance_enabled,
        }

    # -- privacy -------------------------------------------------------------

    def is_pii(self, record: DataRecord) -> bool:
        return bool(self.engine.security.detect_pii(record))

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "policies": len(self._policies),
            "owned_assets": len(self._ownership),
        }


__all__ = ["GovernanceEngine"]
