"""Tests for the governance subsystem (Fase 8)."""

from __future__ import annotations

import pytest

from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import DataClassification
from data_intelligence.governance.audit import AuditTrail
from data_intelligence.governance.base import GovernanceError, PolicyRule
from data_intelligence.governance.compliance import ComplianceChecker
from data_intelligence.governance.engine import GovernanceEngine
from data_intelligence.governance.lineage import DataLineage
from data_intelligence.governance.policy import PolicyManager


def make_governance_engine() -> GovernanceEngine:
    return GovernanceEngine(events=DataIntelligenceEvents(),
                            metrics=DataIntelligenceMetrics(), config=None,
                            context=DataIntelligenceContext())


# ---------------------------------------------------------------------------
# policies
# ---------------------------------------------------------------------------

def test_policy_manager_add_and_resolve():
    manager = PolicyManager()
    manager.add_rule("vendas", action="allow", operation="read")
    manager.add_rule("folha_pagamento", action="deny")
    manager.add_rule("*", action="review")
    assert len(manager.rules_for("vendas", "read")) == 2
    assert [r.action for r in manager.rules_for("folha_pagamento", "read")] == \
        ["deny", "review"]
    assert [r.action for r in manager.rules_for("marketing", "write")] == \
        ["review"]
    assert manager.stats()["rules"] == 3


def test_policy_rule_holds_max_classification():
    rule = PolicyRule(dataset="clientes", action="allow",
                      max_classification=DataClassification.INTERNAL)
    assert rule.max_classification == DataClassification.INTERNAL


# ---------------------------------------------------------------------------
# governance engine: access control
# ---------------------------------------------------------------------------

def test_public_dataset_always_allowed():
    engine = make_governance_engine()
    decision = engine.check_access("anonimo", "catalogo", "read")
    assert decision["decision"] == "allow"
    assert decision["classification"] == "public"


def test_confidential_dataset_denied_without_grant():
    engine = make_governance_engine()
    decision = engine.check_access("analista", "clientes_pii", "read")
    assert decision["decision"] == "deny"
    assert decision["classification"] == "confidential"


def test_grant_unlocks_access():
    engine = make_governance_engine()
    engine.grant("analista", "clientes_pii")
    assert engine.check_access("analista", "clientes_pii",
                               "read")["decision"] == "allow"


def test_explicit_classification_override():
    engine = make_governance_engine()
    engine.register_dataset("vendas", DataClassification.CONFIDENTIAL)
    decision = engine.check_access("equipe", "vendas")
    assert decision["classification"] == "confidential"
    assert decision["decision"] == "deny"


def test_deny_rule_overrides_grant():
    engine = make_governance_engine()
    engine.grant("admin", "vendas_internas")
    engine.add_policy("vendas_internas", action="deny", operation="delete")
    assert engine.check_access("admin", "vendas_internas",
                               "delete")["decision"] == "deny"
    assert engine.check_access("admin", "vendas_internas",
                               "read")["decision"] == "allow"


def test_review_rule():
    engine = make_governance_engine()
    engine.add_policy("novos_dados", action="review", operation="write")
    decision = engine.check_access("cientista", "novos_dados", "write")
    assert decision["decision"] == "review"


def test_max_classification_caps_access():
    engine = make_governance_engine()
    engine.grant("auditor", "dados_health")
    engine.add_policy("dados_health", action="allow",
                      max_classification=DataClassification.INTERNAL)
    decision = engine.check_access("auditor", "dados_health", "read")
    assert decision["decision"] == "deny"  # confidential > internal


def test_access_check_counts_metric():
    engine = make_governance_engine()
    engine.check_access("anonimo", "catalogo")
    snapshot = engine.metrics.snapshot()["counters"]
    assert snapshot["governance.access_checks"] == 1


# ---------------------------------------------------------------------------
# lineage
# ---------------------------------------------------------------------------

def test_lineage_upstream_downstream():
    lineage = DataLineage()
    lineage.add_edge("erp", "bronze", "ingest")
    lineage.add_edge("bronze", "silver", "transform")
    lineage.add_edge("silver", "gold_vendas", "aggregate")
    lineage.add_edge("crm", "gold_clientes", "aggregate")
    assert lineage.upstream("gold_vendas") == {"erp", "bronze", "silver"}
    assert lineage.downstream("bronze") == {"silver", "gold_vendas"}
    assert lineage.path("erp", "gold_vendas") == ["erp", "bronze", "silver",
                                                  "gold_vendas"]
    assert lineage.path("erp", "gold_clientes") == []


def test_lineage_impact():
    lineage = DataLineage()
    lineage.add_edge("bronze", "silver", "transform")
    lineage.add_edge("silver", "dashboard", "aggregate")
    impact = lineage.impact("bronze")
    assert set(impact["affected"]) == {"silver", "dashboard"}
    assert impact["count"] == 2


def test_lineage_stats():
    lineage = DataLineage()
    lineage.add_edge("a", "b")
    lineage.add_edge("b", "c")
    assert lineage.stats()["edges"] == 2
    assert lineage.stats()["datasets"] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# audit trail
# ---------------------------------------------------------------------------

def test_audit_trail_record_and_search():
    trail = AuditTrail()
    trail.record("ana", "read", "vendas", "ok")
    trail.record("ana", "delete", "vendas", "denied")
    trail.record("bia", "read", "clientes", "ok")
    assert trail.count() == 3
    assert len(trail.search(actor="ana")) == 2
    assert len(trail.search(action="read")) == 2
    assert len(trail.search(resource="clientes")) == 1
    assert len(trail.search(actor="ana", action="read")) == 1


def test_audit_trail_counts_and_recent():
    trail = AuditTrail()
    trail.record("a", "read", "x")
    trail.record("a", "read", "y")
    trail.record("b", "write", "z")
    assert trail.counts_by_action() == {"read": 2, "write": 1}
    assert len(trail.recent(2)) == 2


# ---------------------------------------------------------------------------
# compliance
# ---------------------------------------------------------------------------

def test_compliance_checks_required_fields():
    engine = make_governance_engine()
    report = engine.run_compliance(
        "clientes", [{"nome": "Ana"}, {"nome": ""}],
        required_fields=("nome", "email"), pii_fields=())
    assert report["high"] >= 2
    assert report["status"] == "non_compliant"
    assert any("email" in finding["finding"]
               for finding in report["findings"])


def test_compliance_flags_unmasked_pii():
    engine = make_governance_engine()
    report = engine.run_compliance(
        "clientes_pii", [{"email": "ana@empresa.com"}],
        required_fields=(), pii_fields=("email",))
    assert report["high"] == 1
    assert any("PII" in finding["finding"]
               for finding in report["findings"])


def test_compliance_masked_pii_passes():
    engine = make_governance_engine()
    report = engine.run_compliance(
        "clientes_pii",
        [{"email": "a***@empresa.com"}],
        required_fields=(), pii_fields=("email",))
    assert report["status"] == "compliant"
    assert report["findings"] == []


def test_compliance_empty_dataset():
    engine = make_governance_engine()
    report = engine.run_compliance("vazio", [])
    assert report["findings"][0]["finding"] == "dataset vazio"


# ---------------------------------------------------------------------------
# governance engine: integration
# ---------------------------------------------------------------------------

def test_governance_engine_audit_and_lineage():
    engine = make_governance_engine()
    entry = engine.audit_action("ana", "export", "gold_vendas", "ok",
                                {"format": "csv"})
    assert entry["status"] == "ok"
    assert engine.audit.count() == 1
    engine.add_lineage("erp", "bronze")
    engine.add_lineage("bronze", "gold_vendas")
    trace = engine.trace_lineage("gold_vendas")
    assert trace["upstream"] == ["bronze", "erp"]
    assert trace["downstream"] == []


def test_governance_engine_compliance_publishes_event():
    engine = make_governance_engine()
    seen: list[str] = []
    engine.events.on(DataIntelligenceEventType.GOVERNANCE_ACTION,
                     lambda payload: seen.append(
                         str(payload.get("action"))))
    engine.run_compliance("clientes", [{"nome": "Ana"}],
                          required_fields=("nome",))
    assert "compliance_check" in seen
    snapshot = engine.metrics.snapshot()["counters"]
    assert snapshot["governance.compliance"] == 1


def test_governance_engine_stats():
    engine = make_governance_engine()
    engine.register_dataset("vendas", DataClassification.INTERNAL)
    engine.add_policy("vendas", action="allow")
    engine.add_lineage("a", "b")
    engine.audit_action("ana", "read", "vendas")
    stats = engine.stats()
    assert stats["datasets"] == ["vendas"]
    assert stats["policies"] == 1
    assert stats["lineage_edges"] == 1
    assert stats["audit_entries"] == 1
