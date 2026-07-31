"""Tests for the knowledge governance subsystem."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from knowledge.governance import (
    AuditTrail,
    GovernanceEngine,
    Guardrails,
    Policy,
    PolicyManager,
    RetentionPolicy,
)
from knowledge.knowledge_models import KnowledgeItem


class TestAuditTrail:
    def test_record_list_count(self) -> None:
        trail = AuditTrail()
        trail.record("create", actor="alice", item_id="doc-1")
        trail.record("update", actor="bob")
        assert trail.count() == 2
        assert len(trail.list("create")) == 1
        assert len(trail.list("missing")) == 0

    def test_max_entries(self) -> None:
        trail = AuditTrail(max_entries=3)
        for index in range(5):
            trail.record("op", index=index)
        assert trail.count() == 3
        trail.clear()
        assert trail.count() == 0


class TestGuardrails:
    def test_blocked_terms(self) -> None:
        guardrails = Guardrails(blocked_terms=["secret"])
        allowed, reason = guardrails.check("conteudo normal")
        assert allowed is True
        allowed, reason = guardrails.check("this has a secret")
        assert allowed is False
        assert "blocked" in reason

    def test_max_content_chars(self) -> None:
        guardrails = Guardrails(max_content_chars=10)
        assert guardrails.check("x" * 5) == (True, "ok")
        assert guardrails.check("x" * 20)[0] is False

    def test_accepts_knowledge_item(self) -> None:
        guardrails = Guardrails(blocked_terms=["ban"])
        item = KnowledgeItem(content="palavra banida aqui")
        allowed, reason = guardrails.check(item)
        assert allowed is False


class TestPolicyManager:
    def test_add_remove_get(self) -> None:
        manager = PolicyManager()
        manager.add(Policy(name="p1", scope="docs", rules={"retention": "30d"}))
        policy = manager.get("p1")
        assert policy is not None
        assert policy.scope == "docs"
        assert manager.count() == 1
        assert manager.remove("p1") is True
        assert manager.remove("p1") is False

    def test_applies(self) -> None:
        manager = PolicyManager()
        manager.add(Policy(name="global", scope="*"))
        manager.add(Policy(name="local", scope="docs"))
        manager.add(Policy(name="disabled", scope="*", enabled=False))
        assert manager.applies("global", "anything") is True
        assert manager.applies("local", "docs") is True
        assert manager.applies("local", "other") is False
        assert manager.applies("disabled", "anything") is False
        assert manager.applies("missing", "anything") is False

    def test_list_enabled_only(self) -> None:
        manager = PolicyManager()
        manager.add(Policy(name="on", scope="*"))
        manager.add(Policy(name="off", scope="*", enabled=False))
        assert len(manager.list()) == 2
        assert [policy.name for policy in manager.list(enabled_only=True)] == ["on"]


class TestRetentionPolicy:
    def test_is_expired(self) -> None:
        policy = RetentionPolicy(retention_days=30)
        old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        recent = datetime.now(timezone.utc).isoformat()
        assert policy.is_expired(old) is True
        assert policy.is_expired(recent) is False

    def test_invalid_date(self) -> None:
        policy = RetentionPolicy()
        assert policy.is_expired("not-a-date") is False
        assert policy.is_expired("") is False

    def test_filter_expired(self) -> None:
        policy = RetentionPolicy(retention_days=30)

        class StubRecord:
            def __init__(self, created_at: str) -> None:
                self.created_at = created_at

        old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        recent = datetime.now(timezone.utc).isoformat()
        expired = policy.filter_expired([StubRecord(old), StubRecord(recent)])
        assert len(expired) == 1
        assert policy.filter_expired([object()]) == []


class TestGovernanceEngine:
    def test_add_policy_and_validate(self) -> None:
        engine = GovernanceEngine()
        engine.add_policy("retention", scope="*", rules={"days": "30"})
        assert engine.policies.count() == 1
        result = engine.validate("conteudo valido")
        assert result["allowed"] is True
        assert result["reason"] == "ok"

    def test_validate_blocks(self) -> None:
        engine = GovernanceEngine()
        engine.guardrails = Guardrails(blocked_terms=["proibido"])
        result = engine.validate("texto com proibido")
        assert result["allowed"] is False

    def test_audit_action(self) -> None:
        engine = GovernanceEngine()
        engine.audit_action("export", actor="alice", format="csv")
        assert engine.audit.count() == 1
        assert engine.audit.list("export")[0]["format"] == "csv"

    def test_purge_expired(self) -> None:
        engine = GovernanceEngine()
        old = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()
        recent = datetime.now(timezone.utc).isoformat()
        expired = engine.purge_expired([KnowledgeItem(content="velho", created_at=old)])
        assert len(expired) == 1
        assert engine.purge_expired([KnowledgeItem(content="novo", created_at=recent)]) == []

    def test_stats(self) -> None:
        engine = GovernanceEngine()
        engine.validate("texto")
        stats = engine.stats()
        assert stats["policies"] == 0
        assert stats["audit_entries"] >= 1
        assert stats["retention_days"] == 365
