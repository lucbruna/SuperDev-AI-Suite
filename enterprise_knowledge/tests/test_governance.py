"""Tests for the governance subsystem (Fase 10)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.governance import (AccessControl, AuditLogger,
                                             GovernanceClassification,
                                             GovernanceEngine,
                                             RetentionPolicy)
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_models import (AccessLevel, MemoryRecord,
                                                   MemoryType)
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry


@pytest.fixture
def registry():
    return EnterpriseKnowledgeRegistry()


@pytest.fixture
def engine(registry):
    return GovernanceEngine(registry=registry)


@pytest.fixture
def old_memory():
    import time
    return MemoryRecord(
        memory_id="mem-old", content="registro antigo",
        memory_type=MemoryType.EPISODIC, created_at=time.time() - 400 * 86400,
    )


class TestAccessControl:
    def test_allowed_by_rank(self):
        control = AccessControl()
        assert control.allowed("employee", AccessLevel.INTERNAL)
        assert not control.allowed("guest", AccessLevel.INTERNAL)
        assert control.allowed("manager", AccessLevel.CONFIDENTIAL)
        assert control.allowed("admin", AccessLevel.RESTRICTED)

    def test_classify_rank(self):
        assert AccessControl.classify_rank(AccessLevel.PUBLIC) == 0
        assert AccessControl.classify_rank(AccessLevel.RESTRICTED) == 3


class TestGovernanceClassification:
    def test_classify_public(self):
        classifier = GovernanceClassification()
        assert classifier.classify("treinamento geral") == AccessLevel.PUBLIC

    def test_classify_confidential(self):
        classifier = GovernanceClassification()
        assert classifier.classify("dados da folha salarial") == \
            AccessLevel.CONFIDENTIAL

    def test_classify_restricted(self):
        classifier = GovernanceClassification()
        assert classifier.classify("plano estratégico do board") == \
            AccessLevel.RESTRICTED

    def test_add_rule(self):
        classifier = GovernanceClassification()
        classifier.add_rule(AccessLevel.CONFIDENTIAL, ["senha"])
        assert classifier.classify("senha do servidor") == \
            AccessLevel.CONFIDENTIAL


class TestRetentionPolicy:
    def test_default_days(self):
        policy = RetentionPolicy(default_days=30)
        assert policy.days_for() == 30

    def test_override(self):
        policy = RetentionPolicy()
        policy.set_override(AccessLevel.RESTRICTED, 7)
        assert policy.days_for(AccessLevel.RESTRICTED) == 7
        assert policy.days_for() == 365

    def test_purge_expired(self, old_memory):
        import time
        policy = RetentionPolicy(default_days=365)
        fresh = MemoryRecord(memory_id="mem-new", content="recente",
                             memory_type=MemoryType.EPISODIC,
                             created_at=time.time() - 10 * 86400)
        kept = policy.purge([old_memory, fresh])
        assert [record.memory_id for record in kept] == ["mem-new"]


class TestAuditLogger:
    def test_log_with_registry(self, registry):
        logger = AuditLogger(registry)
        entry = logger.log("alice", "access.check", "access:restricted",
                           AccessLevel.RESTRICTED, outcome="denied")
        assert entry is not None
        assert entry.actor == "alice"
        assert logger.count() == 1
        assert logger.recent(1)[0].outcome == "denied"

    def test_log_without_registry(self):
        logger = AuditLogger(None)
        assert logger.log("alice", "access.check") is None
        assert logger.count() == 0


class TestGovernanceEngine:
    def test_policy_lifecycle(self, engine):
        policy = engine.add_policy("pol-acesso", "access",
                                   AccessLevel.CONFIDENTIAL)
        assert policy.policy_id.startswith("pol-")
        assert engine.get_policy(policy.policy_id) is policy
        assert len(engine.list_policies()) == 1
        assert engine.remove_policy(policy.policy_id)
        assert not engine.remove_policy(policy.policy_id)

    def test_check_access_allowed(self, engine):
        assert engine.check_access("admin", AccessLevel.RESTRICTED)

    def test_check_access_denied_audits(self, engine):
        assert not engine.check_access("guest", AccessLevel.RESTRICTED)
        assert engine.audit_count() == 1
        assert engine.recent_audit(1)[0].outcome == "denied"
        assert engine.stats()["access_denied"] == 1

    def test_denial_publishes_event(self, registry):
        events = EnterpriseKnowledgeEvents()
        fired = []
        events.on(EnterpriseKnowledgeEventType.ACCESS_DENIED,
                  lambda payload: fired.append(payload))
        engine = GovernanceEngine(registry=registry, events=events)
        assert not engine.check_access("guest", AccessLevel.RESTRICTED)
        assert len(fired) == 1

    def test_can_rbac(self, engine):
        assert engine.can("admin", "system.shutdown")
        assert not engine.can("employee", "write.document")
        assert engine.can("employee", "search.all")

    def test_classify(self, engine):
        assert engine.classify("relatório sigiloso") == \
            AccessLevel.CONFIDENTIAL

    def test_apply_retention(self, engine, old_memory):
        kept = engine.apply_retention([old_memory])
        assert kept == []
        assert engine.stats()["audit_entries"] == 1
