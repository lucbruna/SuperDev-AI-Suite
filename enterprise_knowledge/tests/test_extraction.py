"""Tests for the extraction/ subsystem (Volume 27, Fase 7)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.extraction.classifier import TextClassifier
from enterprise_knowledge.extraction.entity_extractor import EntityExtractor
from enterprise_knowledge.extraction.extraction_engine import ExtractionEngine
from enterprise_knowledge.extraction.information_parser import InformationParser
from enterprise_knowledge.extraction.relation_extractor import RelationExtractor
from enterprise_knowledge.knowledge_factory import build_engine


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "extraction_engine",
        ExtractionEngine(events=engine.events, metrics=engine.metrics,
                         config=engine.config, security=engine.security))
    return engine


class TestEntityExtractor:
    def test_extracts_person(self):
        extractor = EntityExtractor()
        entities = extractor.extract("O João Silva lidera o projeto.")
        assert any(e["name"] == "João Silva" and e["type"] == "person"
                   for e in entities)

    def test_extracts_acronym_email_date(self):
        extractor = EntityExtractor()
        entities = extractor.extract(
            "SQL do ERP. Contato joao@empresa.com em 12/05/2026")
        types = {e["type"] for e in entities}
        assert "acronym" in types and "email" in types and "date" in types

    def test_no_duplicates(self):
        extractor = EntityExtractor()
        entities = extractor.extract("João Silva falou com João Silva")
        names = [e["name"] for e in entities if e["type"] == "person"]
        assert names.count("João Silva") == 1

    def test_classify_keywords(self):
        extractor = EntityExtractor()
        assert extractor.classify("postgresql") == "database"
        assert extractor.classify("projeto erp") == "project"

    def test_extract_with_types(self):
        extractor = EntityExtractor()
        entities = extractor.extract_with_types(
            "O PostgreSQL é usado no projeto ERP")
        by_name = {e["name"]: e["type"] for e in entities}
        assert by_name.get("PostgreSQL") == "database"


class TestRelationExtractor:
    def test_extracts_relation_with_verb(self):
        extractor = RelationExtractor()
        relations = extractor.extract(
            "O projeto usa o banco PostgreSQL.")
        assert relations
        assert relations[0]["verb"] == "usa"
        assert relations[0]["type"] == "uses"

    def test_subject_and_target(self):
        extractor = RelationExtractor()
        relations = extractor.extract("O João implementa o módulo fiscal")
        assert relations[0]["subject"] == "o joão"
        assert relations[0]["target"] == "o módulo"

    def test_unknown_verb_no_relations(self):
        extractor = RelationExtractor()
        assert extractor.extract("apenas uma frase sem verbo de relação") == []


class TestInformationParser:
    def test_dates(self):
        parser = InformationParser()
        assert parser.dates("Publicado em 10/03/2026") == ["10/03/2026"]

    def test_percentages(self):
        parser = InformationParser()
        assert parser.percentages("crescimento de 25%") == [25.0]

    def test_amounts(self):
        parser = InformationParser()
        amounts = parser.amounts("custo de R$ 1.234,56 no projeto")
        assert any(abs(amount - 1234.56) < 0.01 for amount in amounts)

    def test_numbers(self):
        parser = InformationParser()
        assert parser.numbers("42 usuários em 7 módulos") == [42, 7]

    def test_parse_all(self):
        parser = InformationParser()
        result = parser.parse("Em 01/01/2026 com 10% de lucro")
        assert result["dates"] and result["percentages"] == [10.0]


class TestTextClassifier:
    def test_classifies_code(self):
        result = TextClassifier().classify("def calcular():\n    return sql")
        assert result["category"] == "code"

    def test_classifies_finance(self):
        result = TextClassifier().classify(
            "fatura de imposto para receita")
        assert result["category"] == "finance"

    def test_general_when_unknown(self):
        result = TextClassifier().classify("xyzabc bla")
        assert result["category"] == "general"


class TestExtractionEngine:
    def test_extract_full_pipeline(self, engine):
        result = engine.extraction_engine.extract(
            "O João Silva usa o ERP. O sistema fiscal foi alterado em 2026.")
        assert result.summary
        assert any(e["type"] == "person" for e in result.entities)
        assert result.relations

    def test_metric_and_event(self, engine):
        from enterprise_knowledge.knowledge_events import (
            EnterpriseKnowledgeEventType)
        seen = []
        engine.events.on(EnterpriseKnowledgeEventType.EXTRACTION_COMPLETED,
                         lambda payload: seen.append(payload))
        engine.extraction_engine.extract("O projeto usa o banco PostgreSQL")
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("ek.extractions", 0) == 1
        assert seen and seen[0]["relations"] >= 1

    def test_classify_and_summarize(self, engine):
        assert engine.extraction_engine.classify(
            "o imposto e a fatura fiscal")["category"] == "finance"
        summary = engine.extraction_engine.summarize(
            "Primeira frase aqui. Segunda frase aqui.")
        assert summary.startswith("Primeira frase aqui")

    def test_stats(self, engine):
        engine.extraction_engine.extract("texto qualquer")
        assert engine.extraction_engine.stats().get("ek.extractions", 0) == 1
