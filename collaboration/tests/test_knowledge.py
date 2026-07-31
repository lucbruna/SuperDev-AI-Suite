"""Tests for the knowledge/ subsystem (Volume 26, Fase 7)."""

from __future__ import annotations

import pytest

from collaboration.collaboration_events import CollaborationEventType
from collaboration.collaboration_factory import build_engine
from collaboration.collaboration_models import MemberRole
from collaboration.knowledge.knowledge_engine import KnowledgeEngine


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "knowledge_engine",
        KnowledgeEngine(events=engine.events, metrics=engine.metrics,
                        config=engine.config, security=engine.security,
                        registry=engine.registry))
    return engine


def _setup(engine):
    ws = engine.create_workspace("NEXUS ERP PROJECT", "SP-01")
    owner = engine.add_member(ws.workspace_id, "Carlos Diretor",
                              role=MemberRole.OWNER,
                              email="carlos@nexus.com.br")
    dev = engine.add_member(ws.workspace_id, "Bruno Backend",
                            role=MemberRole.DEVELOPER,
                            email="bruno@nexus.com.br")
    return ws, owner, dev


def test_document_creation(engine):
    ws, owner, dev = _setup(engine)
    document = engine.knowledge_engine.create(
        ws.workspace_id, "Arquitetura do ERP",
        "Microsserviços com API Gateway", dev.member_id,
        tags=["arquitetura", "erp"], category="Arquitetura")
    assert document.document_id.startswith("doc")
    assert document.title == "Arquitetura do ERP"
    assert document.version == 1
    assert document.document_id in engine.knowledge_engine.list()
    assert engine.knowledge_engine.get(document.document_id) is document


def test_document_created_event(engine):
    ws, owner, dev = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.DOCUMENT_CREATED, events.append)
    document = engine.knowledge_engine.create(ws.workspace_id,
                                              "Página Nova", "corpo",
                                              dev.member_id)
    assert events and events[-1]["document_id"] == document.document_id


def test_document_edit_versioning(engine):
    ws, owner, dev = _setup(engine)
    document = engine.knowledge_engine.create(ws.workspace_id,
                                              "Processo de Deploy",
                                              "v1 do processo",
                                              dev.member_id)
    updated = engine.knowledge_engine.edit(document.document_id,
                                           "v2 com automação",
                                           dev.member_id,
                                           tags=["devops"])
    assert updated.version == 2
    assert updated.body == "v2 com automação"
    assert updated.tags == ["devops"]
    history = engine.knowledge_engine.history(document.document_id)
    assert history.count() == 2
    assert history.get(1).body == "v1 do processo"


def test_document_updated_event(engine):
    ws, owner, dev = _setup(engine)
    document = engine.knowledge_engine.create(ws.workspace_id,
                                              "Decisão Técnica", "rascunho",
                                              dev.member_id)
    events = []
    engine.events.on(CollaborationEventType.DOCUMENT_UPDATED, events.append)
    engine.knowledge_engine.edit(document.document_id, "final",
                                 dev.member_id)
    assert events and events[-1]["document_id"] == document.document_id


def test_knowledge_search(engine):
    ws, owner, dev = _setup(engine)
    engine.knowledge_engine.create(ws.workspace_id,
                                   "Arquitetura do ERP",
                                   "API Gateway e filas", dev.member_id,
                                   tags=["arquitetura"])
    engine.knowledge_engine.create(ws.workspace_id,
                                   "Processo de Segurança",
                                   "revisão de acessos", dev.member_id,
                                   tags=["seguranca"])
    results = engine.knowledge_engine.search("arquitetura")
    assert len(results) == 1
    assert results[0].title == "Arquitetura do ERP"


def test_knowledge_search_by_tag(engine):
    ws, owner, dev = _setup(engine)
    engine.knowledge_engine.create(ws.workspace_id, "Guia DevOps",
                                   "pipelines", dev.member_id,
                                   tags=["devops"])
    docs = engine.knowledge_engine.by_tag("devops")
    assert len(docs) == 1
    assert docs[0].title == "Guia DevOps"


def test_knowledge_categories(engine):
    ws, owner, dev = _setup(engine)
    assert "Arquitetura" in engine.knowledge_engine.categories()
    assert engine.knowledge_engine.add_category("UX") is True
    assert engine.knowledge_engine.add_category("UX") is False
    document = engine.knowledge_engine.create(
        ws.workspace_id, "Padrões de Tela", "componentes", dev.member_id,
        category="UX")
    assert document.document_id in \
        engine.knowledge_engine.category_documents("UX")


def test_agent_contributes_to_wiki(engine):
    ws, owner, dev = _setup(engine)
    doc_agent = engine.add_agent(ws.workspace_id, "Documentation IA",
                                 skills=["docs"])
    document = engine.knowledge_engine.create(
        ws.workspace_id, "Manual de Vendas",
        "Redigido pelo agente Documentation", doc_agent.member_id,
        tags=["manual"])
    assert document.author_id == doc_agent.member_id
    assert engine.knowledge_engine.get(document.document_id).title \
        == "Manual de Vendas"


def test_document_remove(engine):
    ws, owner, dev = _setup(engine)
    document = engine.knowledge_engine.create(ws.workspace_id,
                                              "Rascunho Antigo", "x",
                                              dev.member_id)
    document_id = document.document_id
    assert engine.knowledge_engine.remove(document_id) is True
    assert engine.knowledge_engine.get(document_id) is None


def test_knowledge_stats(engine):
    ws, owner, dev = _setup(engine)
    engine.knowledge_engine.create(ws.workspace_id, "Doc 1", "a",
                                   dev.member_id)
    engine.knowledge_engine.create(ws.workspace_id, "Doc 2", "b",
                                   dev.member_id)
    stats = engine.knowledge_engine.stats()
    assert stats["documents"] >= 2
    assert stats["categories"] >= 6
