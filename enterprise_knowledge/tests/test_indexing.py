"""Tests for the indexing/ subsystem (Volume 27, Fase 9)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.indexing.crawler import KnowledgeCrawler
from enterprise_knowledge.indexing.indexing_engine import IndexingEngine
from enterprise_knowledge.indexing.scheduler import IndexScheduler
from enterprise_knowledge.indexing.synchronization import IndexSynchronization
from enterprise_knowledge.indexing.updater import IndexUpdater
from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "indexing_engine",
        IndexingEngine(events=engine.events, metrics=engine.metrics,
                       config=engine.config, security=engine.security,
                       registry=engine.registry))
    return engine


class TestKnowledgeCrawler:
    def test_crawl_single_source(self):
        crawler = KnowledgeCrawler()
        crawler.add_source("wiki", [
            {"document_id": "doc-1", "content": "sistema fiscal"},
        ])
        documents = crawler.crawl()
        assert documents[0]["document_id"] == "doc-1"
        assert documents[0]["source_id"] == "wiki"

    def test_crawl_generates_ids(self):
        crawler = KnowledgeCrawler()
        crawler.add_source("repo", [{"title": "sem id", "content": "x"}])
        assert crawler.crawl()[0]["document_id"].startswith("doc-")

    def test_crawl_filter_by_source(self):
        crawler = KnowledgeCrawler()
        crawler.add_source("a", [{"content": "1"}])
        crawler.add_source("b", [{"content": "2"}])
        assert len(crawler.crawl("a")) == 1
        assert crawler.source_count() == 2


class TestIndexUpdater:
    def test_build_terms_counts(self):
        updater = IndexUpdater()
        terms = updater.build_terms("o sistema fiscal e o sistema fiscal")
        assert terms["sistema"] == 2 and terms["fiscal"] == 2
        assert "o" not in terms and "e" not in terms

    def test_standalone_returns_none(self):
        assert IndexUpdater().upsert("doc-1", "texto") is None

    def test_upsert_and_mark_stale(self):
        registry = EnterpriseKnowledgeRegistry()
        updater = IndexUpdater(registry=registry)
        entry = updater.upsert("doc-1", "conteúdo do contrato")
        assert entry is not None
        assert entry.index_id.startswith("idx-")
        assert entry.terms["contrato"] == 1
        assert updater.mark_stale("doc-1") is True
        assert entry.status.value == "stale"


class TestIndexScheduler:
    def test_due_by_frequency(self):
        scheduler = IndexScheduler(frequency_seconds=100)
        assert scheduler.due(now=200.0) is True
        scheduler.trigger(lambda: None)
        assert scheduler.due(now=250.0) is False

    def test_run_if_due(self):
        scheduler = IndexScheduler(frequency_seconds=10)
        ran = []
        assert scheduler.run_if_due(lambda: ran.append(1), now=100.0) is True
        assert scheduler.run_if_due(lambda: ran.append(1), now=105.0) is False
        assert ran == [1]
        assert scheduler.runs == 1

    def test_trigger(self):
        scheduler = IndexScheduler()
        runs = []
        scheduler.trigger(lambda: runs.append("ok"))
        assert runs == ["ok"] and scheduler.runs == 1


class TestIndexSynchronization:
    def test_diff(self):
        sync = IndexSynchronization()
        diff = sync.diff(["doc-1", "doc-3"], [
            {"document_id": "doc-1"}, {"document_id": "doc-2"},
        ])
        assert diff["to_index"] == ["doc-2"]
        assert diff["to_remove"] == ["doc-3"]
        assert diff["synced"] == ["doc-1"]
        assert sync.needs_refresh(diff) is True

    def test_no_changes(self):
        sync = IndexSynchronization()
        diff = sync.diff(["a"], [{"document_id": "a"}])
        assert sync.needs_refresh(diff) is False


class TestIndexingEngine:
    def test_refresh_indexes_new_source(self, engine):
        engine.indexing_engine.add_source("wiki", [
            {"document_id": "doc-1", "content": "manual do ERP"},
        ])
        result = engine.indexing_engine.refresh()
        assert result["indexed"] == 1
        index_ids = engine.registry.list_index()
        assert len(index_ids) == 1
        assert index_ids[0].startswith("idx-")

    def test_refresh_is_idempotent(self, engine):
        engine.indexing_engine.add_source("wiki", [
            {"document_id": "doc-1", "content": "manual"},
        ])
        engine.indexing_engine.refresh()
        result = engine.indexing_engine.refresh()
        assert result["indexed"] == 0

    def test_refresh_removes_missing(self, engine):
        engine.indexing_engine.add_source("wiki", [
            {"document_id": "doc-1", "content": "manual"},
        ])
        engine.indexing_engine.refresh()
        engine.indexing_engine.crawler.add_source(
            "wiki", [{"document_id": "doc-1", "content": "manual"}])
        engine.indexing_engine.crawler._sources["wiki"] = []  # doc removed
        result = engine.indexing_engine.refresh()
        assert result["removed"] == 1
        assert engine.registry.list_index() == []

    def test_search_index(self, engine):
        engine.indexing_engine.add_source("repo", [
            {"document_id": "doc-1",
             "content": "o sistema fiscal e o sistema fiscal"},
            {"document_id": "doc-2", "content": "sistema de bolo"},
        ])
        engine.indexing_engine.refresh()
        hits = engine.indexing_engine.search_index("sistema")
        assert len(hits) == 2
        assert hits[0]["target_id"] == "doc-1"

    def test_metric_and_event(self, engine):
        from enterprise_knowledge.knowledge_events import (
            EnterpriseKnowledgeEventType)
        seen = []
        engine.events.on(EnterpriseKnowledgeEventType.INDEX_UPDATED,
                         lambda payload: seen.append(payload))
        engine.indexing_engine.add_source("a", [{"content": "texto"}])
        engine.indexing_engine.refresh()
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("ek.index_entries", 0) == 1
        assert seen and seen[0]["indexed"] == 1

    def test_stats(self, engine):
        engine.indexing_engine.add_source("a", [{"content": "x"}])
        engine.indexing_engine.refresh()
        stats = engine.indexing_engine.stats()
        assert stats["sources"] == 1 and stats["entries"] == 1
