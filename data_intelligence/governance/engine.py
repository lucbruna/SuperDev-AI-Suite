"""Governance engine (attached by the facade as ``governance``).

Coordinates access policies, data lineage, audit trail and LGPD-style
compliance checks on top of the security layer.
"""

from __future__ import annotations

from typing import Any

from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import DataClassification
from data_intelligence.data_security import DataIntelligenceSecurity
from data_intelligence.governance.audit import AuditTrail
from data_intelligence.governance.base import (CLASSIFICATION_LEVELS,
                                               PolicyRule)
from data_intelligence.governance.compliance import ComplianceChecker
from data_intelligence.governance.lineage import DataLineage
from data_intelligence.governance.policy import PolicyManager


class GovernanceEngine:
    """Coordinates policies, lineage, audits and compliance."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any, security: DataIntelligenceSecurity | None = None) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.security = security or DataIntelligenceSecurity()
        self.policy = PolicyManager()
        self.lineage = DataLineage()
        self.audit = AuditTrail()
        self.compliance = ComplianceChecker(self.security)
        self.classifications: dict[str, DataClassification] = {}

    def register_dataset(self, dataset: str,
                         classification: DataClassification) -> None:
        self.classifications[dataset] = classification
        self.metrics.increment("governance.datasets")

    def add_policy(self, dataset: str, action: str = "allow",
                   operation: str = "*",
                   max_classification: DataClassification | None = None) -> PolicyRule:
        rule = self.policy.add_rule(dataset, action, operation,
                                    max_classification)
        self.metrics.increment("governance.policies")
        return rule

    def check_access(self, role: str, dataset: str,
                     operation: str = "read") -> dict[str, Any]:
        """Decides allow/deny/review using classification, grants and rules."""
        classification = self.classifications.get(
            dataset, self.security.classify(dataset))
        decision = "deny"
        if classification == DataClassification.PUBLIC or \
                self.security.can_access(role, dataset):
            decision = "allow"
        for rule in self.policy.rules_for(dataset, operation):
            if rule.max_classification is not None and \
                    CLASSIFICATION_LEVELS[classification] > \
                    CLASSIFICATION_LEVELS[rule.max_classification]:
                decision = "deny"
            elif rule.action == "deny":
                decision = "deny"
            elif rule.action == "review" and decision != "deny":
                decision = "review"
        self.security.audit(role, operation, dataset)
        self.metrics.increment("governance.access_checks")
        return {"dataset": dataset, "role": role, "operation": operation,
                "classification": classification.value, "decision": decision}

    def grant(self, role: str, dataset: str) -> None:
        self.security.grant(role, dataset)

    def audit_action(self, actor: str, action: str, resource: str,
                     status: str = "ok",
                     detail: dict[str, Any] | None = None) -> dict[str, Any]:
        entry = self.audit.record(actor, action, resource, status, detail)
        self.events.publish(DataIntelligenceEventType.GOVERNANCE_ACTION,
                            {"actor": actor, "action": action,
                             "resource": resource, "status": status})
        self.metrics.increment("governance.audits")
        return entry

    def add_lineage(self, source: str, target: str,
                    operation: str = "derived") -> None:
        self.lineage.add_edge(source, target, operation)
        self.metrics.increment("governance.lineage_edges")

    def trace_lineage(self, dataset: str) -> dict[str, Any]:
        return {"dataset": dataset,
                "upstream": sorted(self.lineage.upstream(dataset)),
                "downstream": sorted(self.lineage.downstream(dataset))}

    def impact_analysis(self, dataset: str) -> dict[str, Any]:
        return self.lineage.impact(dataset)

    def run_compliance(self, dataset: str, records: list[dict[str, Any]],
                       required_fields: tuple[str, ...] = (),
                       pii_fields: tuple[str, ...] = ()) -> dict[str, Any]:
        report = self.compliance.check(dataset, records, required_fields,
                                       pii_fields)
        self.audit.record("system", "compliance_check", dataset,
                          status=report["status"])
        self.events.publish(DataIntelligenceEventType.GOVERNANCE_ACTION,
                            {"action": "compliance_check", "resource": dataset,
                             "status": report["status"]})
        self.metrics.increment("governance.compliance")
        return report

    def stats(self) -> dict[str, Any]:
        return {"datasets": sorted(self.classifications),
                "policies": self.policy.stats()["rules"],
                "lineage_edges": self.lineage.stats()["edges"],
                "audit_entries": self.audit.count(),
                "compliance_status": sorted(
                    {entry["status"] for entry in self.audit.search(
                        action="compliance_check")})}
