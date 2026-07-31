from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import KnowledgeItem
from .audit_trail import AuditTrail
from .guardrails import Guardrails
from .policy_manager import Policy, PolicyManager
from .retention_policy import RetentionPolicy


class GovernanceEngine:
    """Composes policies, guardrails, audit, and retention enforcement."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.governance.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.policies = PolicyManager()
        self.guardrails = Guardrails()
        self.audit = AuditTrail()
        self.retention = RetentionPolicy(self.config.retention_days)

    def add_policy(self, name: str, scope: str = "*", rules: dict[str, str] | None = None) -> None:
        self.policies.add(Policy(name=name, scope=scope, rules=rules or {}))

    def validate(self, item: KnowledgeItem | str) -> dict[str, Any]:
        allowed, reason = self.guardrails.check(item)
        result = {"allowed": allowed, "reason": reason}
        self.audit.record("validate", actor="engine", allowed=allowed, reason=reason)
        self.metrics.increment("governance.validated")
        return result

    def audit_action(self, action: str, actor: str = "system", **details: Any) -> None:
        self.audit.record(action, actor, **details)

    def purge_expired(self, records: list[Any]) -> list[Any]:
        expired = self.retention.filter_expired(records)
        self.audit.record("purge", actor="retention", count=len(expired))
        self.events.emit(KnowledgeEventType.MEMORY_PRUNED, {"expired": len(expired)})
        return expired

    def stats(self) -> dict[str, Any]:
        return {
            "policies": self.policies.count(),
            "audit_entries": self.audit.count(),
            "retention_days": self.retention.retention_days,
        }
