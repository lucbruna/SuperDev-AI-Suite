"""Tests for the documents/ subsystem (Volume 27, Fase 4)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.documents.classification import DocumentClassifier
from enterprise_knowledge.documents.document_engine import DocumentEngine
from enterprise_knowledge.documents.document_manager import DocumentManager
from enterprise_knowledge.documents.extractor import EntityExtractor
from enterprise_knowledge.documents.metadata import MetadataExtractor
from enterprise_knowledge.documents.parser import DocumentParser
from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.knowledge_models import DocumentStatus
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry
from enterprise_knowledge.vector.vector_engine import VectorEngine


@pytest.fixture
def engine():
    engine = build_engine()
    vectors = VectorEngine(events=engine.events, metrics=engine.metrics,
                           config=engine.config, security=engine.security,
                           registry=engine.registry)
    engine.attach_subsystem("vector_engine", vectors)
    engine.attach_subsystem(
        "document_engine",
        DocumentEngine(events=engine.events, metrics=engine.metrics,
                       config=engine.config, security=engine.security,
                       registry=engine.registry, vectors=vectors))
    return engine


class TestDocumentParser:
    def test_plain_text(self):
        parsed = DocumentParser().parse("nota.txt", "conteúdo simples")
        assert parsed["title"] == "nota.txt"
        assert parsed["content"] == "conteúdo simples"
        assert parsed["file_type"] == "txt"

    def test_html_stripped(self):
        parsed = DocumentParser().parse(
            "pagina.html",
            "<html><body><script>alert(1)</script>"
            "<style>body{color:red}</style><p>Olá</p></body></html>")
        assert "<script>" not in parsed["content"]
        assert "Olá" in parsed["content"]

    def test_json_flattened(self):
        parsed = DocumentParser().parse(
            "dados.json", '{"nome": "ERP", "modulos": ["fiscal", "banco"]}')
        assert "ERP" in parsed["content"]

    def test_unknown_extension_content(self):
        parsed = DocumentParser().parse("arquivo.xyz", "raw")
        assert parsed["content"] == "raw" and parsed["file_type"] == "xyz"

    def test_size_limit(self):
        parser = DocumentParser(max_size=10)
        assert len(parser.parse("a.txt", "x" * 100)["content"]) == 10


class TestMetadataExtractor:
    def test_basic_fields(self):
        meta = MetadataExtractor().extract(
            "Relatório do sistema\nCom dados de fatura para análise.",
            title="Relatório do sistema")
        assert meta["title"] == "Relatório do sistema"
        assert meta["word_count"] >= 5
        assert meta["characters"] > 0

    def test_detects_pt(self):
        meta = MetadataExtractor().extract("Não há problema com este texto")
        assert meta["language"] == "pt-BR"

    def test_detects_urls_and_emails(self):
        meta = MetadataExtractor().extract(
            "contato@empresa.com.br https://site.com/a")
        assert meta["has_emails"] is True
        assert meta["has_urls"] is True

    def test_keywords_exclude_stopwords(self):
        meta = MetadataExtractor()
        keywords = meta.keywords("o sistema fiscal e o sistema fiscal")
        assert "sistema" in keywords and "fiscal" in keywords
        assert "o" not in keywords and "e" not in keywords

    def test_title_from_first_line(self):
        meta = MetadataExtractor().extract("Primeira linha curta")
        assert meta["title"] == "Primeira linha curta"


class TestDocumentClassifier:
    def test_classifies_code(self):
        result = DocumentClassifier().classify(
            "def calcular_imposto():\n    return 0")
        assert result["category"] == "code"

    def test_classifies_contract(self):
        result = DocumentClassifier().classify(
            "Contrato firmado entre partes com cláusula de vigência")
        assert result["category"] == "contract"

    def test_general_when_unknown(self):
        result = DocumentClassifier().classify("xyzabc blah")
        assert result["category"] == "general"

    def test_summary(self):
        classifier = DocumentClassifier()
        summary = classifier.summarize(
            "Primeira frase aqui. Segunda frase aqui. Terceira frase aqui.")
        assert summary.startswith("Primeira frase aqui")
        assert summary.count(". ") >= 1


class TestDocumentManager:
    def test_standalone_returns_none(self):
        manager = DocumentManager()
        assert manager.register("sem registry") is None
        assert manager.list() == []

    def test_crud_with_registry(self):
        registry = EnterpriseKnowledgeRegistry()
        manager = DocumentManager(registry=registry)
        document = manager.register("contrato.pdf", content="texto",
                                    file_type="pdf")
        assert document is not None
        assert document.document_id.startswith("doc-")
        assert manager.get(document.document_id) is document
        assert manager.list() == [document.document_id]
        assert manager.update(document.document_id, title="renomeado")
        stored = manager.get(document.document_id)
        assert stored is not None and stored.title == "renomeado"
        assert manager.set_status(document.document_id,
                                  DocumentStatus.INDEXED)
        assert manager.remove(document.document_id) is True


class TestEntityExtractor:
    def test_extracts_person_and_acronym(self):
        extractor = EntityExtractor()
        result = extractor.extract(
            "O João Silva usa o SQL do ERP para o banco de dados")
        names = {e["name"] for e in result["entities"]}
        assert "João Silva" in names
        assert "ERP" in names
        assert result["relations"]

    def test_classify_entity(self):
        extractor = EntityExtractor()
        from enterprise_knowledge.knowledge_models import NodeType
        assert extractor.classify_entity("banco") == NodeType.DATABASE
        assert extractor.classify_entity("desconhecido") == NodeType.CONCEPT


class TestDocumentEngine:
    def test_ingest_txt(self, engine):
        result = engine.document_engine.ingest(
            "nota.txt", "Sistema fiscal alterado em 2026 para nova regra.")
        assert result["document_id"].startswith("doc-")
        assert result["file_type"] == "txt"
        assert result["classification"]["category"] == "finance"
        assert engine.registry.list_documents()

    def test_ingest_indexes_into_vectors(self, engine):
        result = engine.document_engine.ingest(
            "relatorio.txt", "Relatório de performance do PostgreSQL")
        doc_id = result["document_id"]
        assert engine.document_engine.get(doc_id)["status"] == \
            DocumentStatus.INDEXED.value
        assert engine.vector_engine.database.count() >= 1

    def test_find_returns_document(self, engine):
        engine.document_engine.ingest(
            "erp.txt", "Manual do módulo fiscal do ERP")
        engine.document_engine.ingest(
            "cafe.txt", "Receita de bolo de chocolate")
        hits = engine.document_engine.find("módulo fiscal")
        assert hits
        assert hits[0]["document_id"].startswith("doc-")

    def test_metrics_and_events(self, engine):
        from enterprise_knowledge.knowledge_events import (
            EnterpriseKnowledgeEventType)
        seen = []
        engine.events.on(EnterpriseKnowledgeEventType.DOCUMENT_INDEXED,
                         lambda payload: seen.append(payload))
        engine.document_engine.ingest("x.txt", "conteúdo de teste")
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("ek.documents", 0) >= 1
        assert any(payload.get("title") for payload in seen)

    def test_remove(self, engine):
        result = engine.document_engine.ingest("tmp.txt", "temp")
        assert engine.document_engine.remove(result["document_id"]) is True
        assert engine.document_engine.list_documents() == []

    def test_list_and_stats(self, engine):
        engine.document_engine.ingest("a.txt", "primeiro")
        engine.document_engine.ingest("b.txt", "segundo")
        assert len(engine.document_engine.list_documents()) == 2
        assert engine.document_engine.stats()["documents"] == 2
