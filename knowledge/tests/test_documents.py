"""Tests for the knowledge documents subsystem."""

from __future__ import annotations

import pytest

from knowledge.documents import (
    DocumentEngine,
    DocumentMetadata,
    DocumentVersioning,
    InMemoryDocumentManager,
    Parser,
)
from knowledge.knowledge_models import DocumentRecord


class TestDocumentMetadata:
    def test_build(self) -> None:
        metadata = DocumentMetadata()
        result = metadata.build(title="Manual", doc_type="guide", author="Ana", tags=["api"])
        assert result["title"] == "Manual"
        assert result["doc_type"] == "guide"
        assert result["author"] == "Ana"
        assert result["tags"] == ["api"]

    def test_tags_from_text(self) -> None:
        metadata = DocumentMetadata()
        tags = metadata.tags_from_text("deploy the api to production")
        assert "deploy" in tags
        assert "api" in tags


class TestDocumentVersioning:
    def test_snapshot_history_count(self) -> None:
        versioning = DocumentVersioning()
        versioning.snapshot("doc-1", "v1 content", version=1)
        versioning.snapshot("doc-1", "v2 content", version=2)
        assert versioning.count("doc-1") == 2
        history = versioning.history("doc-1")
        assert history[-1]["content"] == "v2 content"
        assert history[-1]["version"] == 2

    def test_previous(self) -> None:
        versioning = DocumentVersioning()
        versioning.snapshot("doc-1", "alpha", version=1)
        versioning.snapshot("doc-1", "beta", version=2)
        previous = versioning.previous("doc-1", current_version=2)
        assert previous is not None
        assert previous["content"] == "alpha"

    def test_unknown_document(self) -> None:
        versioning = DocumentVersioning()
        assert versioning.history("missing") == []
        assert versioning.previous("missing", current_version=5) is None
        assert versioning.count("missing") == 0


class TestInMemoryDocumentManager:
    def test_add_get_list(self) -> None:
        manager = InMemoryDocumentManager()
        document_id = manager.add(DocumentRecord(title="T", content="c"))
        assert document_id == "doc-1"
        document = manager.get(document_id)
        assert document is not None
        assert document.content == "c"
        assert manager.count() == 1
        assert len(manager.list()) == 1

    def test_update_delete(self) -> None:
        manager = InMemoryDocumentManager()
        document_id = manager.add(DocumentRecord(title="T", content="old"))
        updated = DocumentRecord(title="T", content="new")
        assert manager.update(document_id, updated) is True
        updated_doc = manager.get(document_id)
        assert updated_doc is not None
        assert updated_doc.content == "new"
        assert manager.update("missing", updated) is False
        assert manager.delete(document_id) is True
        assert manager.delete(document_id) is False

    def test_search_title(self) -> None:
        manager = InMemoryDocumentManager()
        manager.add(DocumentRecord(title="Relatorio Financeiro", content="x"))
        matches = manager.search_title("relatorio")
        assert len(matches) == 1
        assert matches[0].title == "Relatorio Financeiro"

    def test_serialization_roundtrip(self) -> None:
        manager = InMemoryDocumentManager()
        manager.add(DocumentRecord(title="T", content="saved"))
        data = manager.to_dict()
        restored = InMemoryDocumentManager()
        restored.load_dict(data)
        assert restored.count() == 1
        assert list(restored.list())[0].content == "saved"


class TestParser:
    def test_parse_plain_text(self, tmp_path) -> None:
        parser = Parser()
        path = tmp_path / "manual.txt"
        path.write_text("manual content", encoding="utf-8")
        document = parser.parse(str(path))
        assert document.content == "manual content"
        assert document.doc_type == "text"
        assert document.title == "manual"

    def test_parse_missing_file(self) -> None:
        parser = Parser()
        with pytest.raises(FileNotFoundError):
            parser.parse("nope/does-not-exist.txt")


class TestDocumentEngine:
    def test_add_and_get(self) -> None:
        engine = DocumentEngine()
        document_id = engine.add_document(DocumentRecord(title="Manual", content="conteudo"))
        assert document_id == "doc-1"
        document = engine.get(document_id)
        assert document is not None
        assert document.content == "conteudo"
        assert engine.stats()["documents"] == 1

    def test_update_snapshot(self) -> None:
        engine = DocumentEngine()
        document_id = engine.add_document(DocumentRecord(title="Manual", content="v1"))
        document = engine.get(document_id)
        assert document is not None
        assert engine.update(document_id, document) is True
        updated_doc = engine.get(document_id)
        assert updated_doc is not None
        assert updated_doc.version == 2
        assert engine.versioning.count(document_id) == 2

    def test_add_file(self, tmp_path) -> None:
        engine = DocumentEngine()
        path = tmp_path / "notas.txt"
        path.write_text("notas sobre o projeto", encoding="utf-8")
        document_id = engine.add_file(str(path))
        document = engine.get(document_id)
        assert document is not None
        assert document.content == "notas sobre o projeto"

    def test_parse_file(self, tmp_path) -> None:
        engine = DocumentEngine()
        path = tmp_path / "arquivo.txt"
        path.write_text("texto", encoding="utf-8")
        document = engine.parse_file(str(path))
        assert document.content == "texto"

    def test_missing_document_returns_none(self) -> None:
        engine = DocumentEngine()
        assert engine.get("missing") is None
