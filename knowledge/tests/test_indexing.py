"""Tests for the knowledge indexing subsystem."""

from __future__ import annotations

import pytest

from knowledge.indexing import (
    IndexManager,
    IndexUpdater,
    Indexer,
    IndexingEngine,
    InvertedIndex,
    MetadataIndex,
)
from knowledge.knowledge_models import Chunk, DocumentRecord


class TestInvertedIndex:
    def test_add_search(self) -> None:
        index = InvertedIndex()
        index.add("doc-1", "busca vetorial com python")
        index.add("doc-2", "busca por palavras")
        results = index.search("busca python")
        assert results[0][0] == "doc-1"
        assert results[0][1] > 0

    def test_remove_and_count(self) -> None:
        index = InvertedIndex()
        index.add("doc-1", "alpha beta")
        index.add("doc-2", "gamma delta")
        assert index.count() == 4
        index.remove("doc-1")
        assert index.search("alpha") == []
        index.clear()
        assert index.count() == 0


class TestMetadataIndex:
    def test_add_get_filter(self) -> None:
        index = MetadataIndex()
        index.add("doc-1", {"lang": "pt", "topic": "rag"})
        index.add("doc-2", {"lang": "en"})
        assert index.get("doc-1")["lang"] == "pt"
        assert index.get("missing") == {}
        assert index.filter({"lang": "pt"}) == ["doc-1"]
        assert len(index.filter()) == 2

    def test_remove_and_count(self) -> None:
        index = MetadataIndex()
        index.add("doc-1", {"a": 1})
        index.remove("doc-1")
        assert index.count() == 0
        index.clear()
        assert index.count() == 0


class TestIndexManager:
    def test_add_search_stats(self) -> None:
        manager = IndexManager()
        manager.add("doc-1", "conteudo para indexar", {"lang": "pt"})
        hits = manager.keyword.search("indexar")
        assert hits[0][0] == "doc-1"
        assert manager.metadata.get("doc-1")["lang"] == "pt"
        stats = manager.stats()
        assert stats["keyword_terms"] >= 1
        assert stats["metadata_documents"] == 1

    def test_register_custom_index(self) -> None:
        manager = IndexManager()
        custom = InvertedIndex()
        manager.register("extra", custom)
        assert manager.get("extra") is custom
        assert manager.names() == ["extra"]
        manager.add("doc-1", "texto extra")
        assert custom.search("texto")[0][0] == "doc-1"
        manager.remove("doc-1")
        assert custom.search("texto") == []

    def test_clear(self) -> None:
        manager = IndexManager()
        manager.add("doc-1", "conteudo")
        manager.clear()
        assert manager.stats()["metadata_documents"] == 0


class TestIndexer:
    def test_index_document(self) -> None:
        indexer = Indexer()
        document = DocumentRecord(title="Manual", content="conteudo do manual")
        document_id = indexer.index_document(document)
        assert document_id == "Manual"
        assert indexer.index_manager.metadata.count() == 1

    def test_index_chunk(self) -> None:
        indexer = Indexer()
        chunk = Chunk(text="parte do documento", document_id="doc-1", index=0)
        document_id = indexer.index_chunk(chunk)
        assert document_id == "doc-1"
        assert len(indexer.index_chunks([chunk])) == 1

    def test_remove(self) -> None:
        indexer = Indexer()
        indexer.index_chunk(Chunk(text="x", document_id="doc-1"))
        indexer.remove("doc-1")
        assert indexer.index_manager.metadata.count() == 0


class TestIndexUpdater:
    def test_add_update_remove(self) -> None:
        updater = IndexUpdater()
        updater.add("doc-1", "conteudo original")
        assert updater.keyword_search("original")[0]["document_id"] == "doc-1"
        updater.update("doc-1", "conteudo novo")
        assert updater.keyword_search("novo")[0]["document_id"] == "doc-1"
        assert updater.keyword_search("original") == []
        updater.remove("doc-1")
        assert updater.keyword_search("novo") == []


class TestIndexingEngine:
    def test_add_document_and_search(self) -> None:
        engine = IndexingEngine()
        document = DocumentRecord(title="Manual", content="como configurar o deploy")
        engine.add_document(document)
        hits = engine.search("deploy")
        assert hits[0]["document_id"] == "Manual"
        assert hits[0]["score"] > 0

    def test_add_chunks(self) -> None:
        engine = IndexingEngine()
        chunks = [Chunk(text="primeiro bloco", document_id="doc-1", index=0)]
        engine.add_chunks(chunks)
        assert engine.search("primeiro")[0]["document_id"] == "doc-1"

    def test_stats_and_clear(self) -> None:
        engine = IndexingEngine()
        engine.add_document(DocumentRecord(title="T", content="conteudo do teste"))
        stats = engine.stats()
        assert stats["metadata_documents"] == 1
        engine.clear()
        assert engine.stats()["metadata_documents"] == 0
