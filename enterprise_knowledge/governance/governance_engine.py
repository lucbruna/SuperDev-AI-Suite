"""Governance engine: policies, access checks, audit trail."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.governance.access_control import AccessControl
from enterprise_knowledge.governance.auditing import AuditLogger
from enterprise_knowledge.governance.classification import GovernanceClassification
from enterprise_knowledge.governance.retention import RetentionPolicy
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import (AccessLevel, AuditRecord,
                                                   GovernancePolicy,
                                                   MemoryRecord)
from enterprise_knowledge.knowledge_protocols import new_id
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity


class GovernanceEngine:
    """Orchestrates access, classification, retention and auditing."""

    def __init__(self,
                 registry: EnterpriseKnowledgeRegistry | None = None,
                 events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None) -> None:
        self.registry = registry
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.security = EnterpriseKnowledgeSecurity()
        self.access = AccessControl(self.security)
        self.classification = GovernanceClassification()
        self.retention = RetentionPolicy()
        self.audit = AuditLogger(registry)
        self._policies: dict[str, GovernancePolicy] = {}

    # -- policies ------------------------------------------------------------
    def add_policy(self, name: str, policy_type: str = "access",
                   access_level: AccessLevel = AccessLevel.INTERNAL,
                   retention_days: int = 0,
                   rules: dict[str, Any] | None = None) -> GovernancePolicy:
        policy = GovernancePolicy(
            policy_id=new_id("pol"), name=name, policy_type=policy_type,
            access_level=access_level, retention_days=retention_days,
            rules=rules or {})
        self._policies[policy.policy_id] = policy
        return policy

    def get_policy(self, policy_id: str) -> GovernancePolicy | None:
        return self._policies.get(policy_id)

    def list_policies(self) -> list[GovernancePolicy]:
        return list(self._policies.values())

    def remove_policy(self, policy_id: str) -> bool:
        return self._policies.pop(policy_id, None) is not None

    # -- access checks -------------------------------------------------------
    def check_access(self, role: str, level: AccessLevel) -> bool:
        allowed = self.access.allowed(role, level)
        if not allowed:
            self.events.publish(EnterpriseKnowledgeEventType.ACCESS_DENIED, {
                "actor": role, "target": f"access:{level.value}",
            })
            self.metrics.increment("ek.access_denied")
            self.audit.log(role, "access.check", f"access:{level.value}",
                           level, outcome="denied")
        return allowed

    def can(self, role: str, permission: str) -> bool:
        return self.security.can(role, permission)

    # -- classification ------------------------------------------------------
    def classify(self, text: str) -> AccessLevel:
        level = self.classification.classify(text)
        self.metrics.increment("ek.classifications")
        return level

    # -- retention -----------------------------------------------------------
    def apply_retention(self, records: list[MemoryRecord],
                        now: float | None = None) -> list[MemoryRecord]:
        kept = self.retention.purge(records, now)
        removed = len(records) - len(kept)
        if removed:
            self.metrics.increment("ek.retention_purged", removed)
            self.events.publish(EnterpriseKnowledgeEventType.GOVERNANCE_ACTION, {
                "action": "retention.purge", "removed": removed,
            })
            self.audit.log("system", "retention.purge",
                           f"removed={removed}", outcome="allowed")
        return kept

    # -- audit ---------------------------------------------------------------
    def recent_audit(self, limit: int = 10) -> list[AuditRecord]:
        return self.audit.recent(limit)

    def audit_count(self) -> int:
        return self.audit.count()

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "policies": len(self._policies),
            "audit_entries": self.audit_count(),
            "classifications": self.metrics.snapshot()["counters"].get(
                "ek.classifications", 0),
            "access_denied": self.metrics.snapshot()["counters"].get(
                "ek.access_denied", 0),
        }
