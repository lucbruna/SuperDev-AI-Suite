"""Final wiring: engine facade + governance + integration (Fase 12)."""

from __future__ import annotations

import pytest

from enterprise_knowledge import (EnterpriseKnowledgeEngine,
                                  EnterpriseKnowledgeRegistry, build_engine)
from enterprise_knowledge.governance import GovernanceEngine
from enterprise_knowledge.integration import IntegrationEngine
from enterprise_knowledge.knowledge_events import EnterpriseKnowledgeEventType
from enterprise_knowledge.knowledge_models import AccessLevel


@pytest.fixture
def engine():
    return build_engine()


class TestFinalWiring:
    def test_subsystem_attachment(self, engine):
        governance = GovernanceEngine(registry=engine.registry,
                                      events=engine.events,
                                      metrics=engine.metrics)
        integration = IntegrationEngine(events=engine.events,
                                        metrics=engine.metrics)
        engine.attach_subsystem("governance_engine", governance)
        engine.attach_subsystem("integration_engine", integration)
        assert engine.governance_engine is governance
        assert engine.integration_engine is integration
        assert "governance_engine" in engine.stats()["subsystems"]
        assert "integration_engine" in engine.stats()["subsystems"]

    def test_full_pipeline(self, engine):
        node = engine.create_node("Financeiro", access_level=AccessLevel.INTERNAL)
        doc = engine.register_document("Manual do ERP", "manual sigiloso do ERP",
                                       source="wiki")
        memory = engine.store_memory("Lições do projeto financeiro")
        node2 = engine.create_node("ERP")
        engine.create_relationship(node.node_id, node2.node_id)
        assert engine.get_node(node.node_id) is not None
        assert engine.get_document(doc.document_id) is not None
        assert engine.get_memory(memory.memory_id) is not None
        assert engine.connected(node.node_id, node2.node_id)

    def test_governance_through_engine(self, engine):
        governance = GovernanceEngine(registry=engine.registry,
                                      events=engine.events,
                                      metrics=engine.metrics)
        engine.attach_subsystem("governance_engine", governance)
        assert engine.governance_engine.check_access(
            "admin", AccessLevel.RESTRICTED)
        assert not engine.governance_engine.check_access(
            "guest", AccessLevel.RESTRICTED)
        assert engine.governance_engine.audit_count() == 1

    def test_integration_through_engine(self, engine):
        integration = IntegrationEngine(events=engine.events,
                                        metrics=engine.metrics)
        engine.attach_subsystem("integration_engine", integration)
        engine.integration_engine.register_operation(
            "stats", lambda: engine.stats())
        result = engine.integration_engine.handle_api("stats")
        assert result["ok"] is True
        assert "registry" in result["data"]

    def test_events_fire_through_engine(self, engine):
        fired = []
        engine.events.on(EnterpriseKnowledgeEventType.NODE_CREATED,
                         lambda payload: fired.append(payload))
        engine.create_node("Marketing")
        assert len(fired) == 1
        assert fired[0]["node_id"]

    def test_package_imports(self):
        from enterprise_knowledge.governance import (AccessControl,
                                                     AuditLogger,
                                                     GovernanceClassification,
                                                     GovernanceEngine,
                                                     RetentionPolicy)
        from enterprise_knowledge.integration import (ApiBridge, EventRouter,
                                                      IntegrationEngine,
                                                      RestClient,
                                                      WebhookDispatcher)
        assert GovernanceEngine is not None
        assert IntegrationEngine is not None
