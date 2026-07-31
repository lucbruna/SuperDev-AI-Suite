"""Tests for the knowledge ingestion subsystem."""

from __future__ import annotations

import pytest

from knowledge.ingestion import (
    BatchProcessor,
    IngestionEngine,
    IngestionPipeline,
    IngestionTracker,
    Loader,
    Preprocessor,
)
from knowledge.knowledge_models import DocumentRecord


class TestLoader:
    def test_load_text(self) -> None:
        loader = Loader()
        assert loader.load_text("conteudo") == "conteudo"
        assert loader.load_text("") == ""

    def test_load_file(self, tmp_path) -> None:
        loader = Loader()
        path = tmp_path / "arquivo.txt"
        path.write_text("conteudo do arquivo", encoding="utf-8")
        title, content = loader.load_file(str(path))
        assert title == "arquivo.txt"
        assert content == "conteudo do arquivo"

    def test_to_document_and_item(self) -> None:
        loader = Loader()
        document = loader.to_document("Titulo", "corpo", doc_type="text")
        assert document.title == "Titulo"
        assert document.content == "corpo"
        item = loader.to_item("item content")
        assert item.kind == "text"
        assert item.source == "ingestion"


class TestPreprocessor:
    def test_clean_collapses_whitespace(self) -> None:
        preprocessor = Preprocessor()
        assert preprocessor.clean("Hello   world  !") == "Hello world !"

    def test_clean_strips_markdown(self) -> None:
        preprocessor = Preprocessor(strip_markdown=True)
        cleaned = preprocessor.clean("# Titulo **bold**")
        assert "#" not in cleaned
        assert "Titulo bold" in cleaned

    def test_normalize(self) -> None:
        preprocessor = Preprocessor()
        assert preprocessor.normalize("  Hello World  ") == "hello world"
        assert preprocessor.normalize("Hello", lowercase=False) == "Hello"

    def test_truncate(self) -> None:
        preprocessor = Preprocessor()
        assert preprocessor.truncate("a" * 50, 10) == "a" * 10
        assert preprocessor.truncate("short", 100) == "short"
        assert preprocessor.truncate("", 5) == ""


class TestIngestionPipeline:
    def test_stages(self) -> None:
        pipeline = IngestionPipeline()
        assert pipeline.STAGES == ["preprocess", "chunk", "embed"]

    def test_run_produces_chunks_and_embeddings(self) -> None:
        pipeline = IngestionPipeline()
        document = DocumentRecord(title="T", content="Texto para ingestao no pipeline de conhecimento.")
        result = pipeline.run(document)
        assert result["document_id"] == ""
        assert len(result["chunks"]) == 1
        assert len(result["embeddings"]) == 1
        assert len(result["embeddings"][0].vector) == 384


class TestIngestionTracker:
    def test_record_get_status(self) -> None:
        tracker = IngestionTracker()
        tracker.record("doc-1", "done", {"chunks": 2})
        record = tracker.get("doc-1")
        assert record is not None
        assert record["status"] == "done"
        assert tracker.status("doc-1") == "done"
        assert tracker.status("missing") is None

    def test_list_and_stats(self) -> None:
        tracker = IngestionTracker()
        tracker.record("a", "done")
        tracker.record("b", "done")
        tracker.record("c", "failed")
        assert len(tracker.list()) == 3
        assert tracker.stats() == {"done": 2, "failed": 1}
        tracker.reset()
        assert tracker.list() == []


class TestBatchProcessor:
    def test_split(self) -> None:
        processor = BatchProcessor(batch_size=2)
        documents = [DocumentRecord(title=f"D{index}", content="x") for index in range(5)]
        batches = processor.split(documents)
        assert [len(batch) for batch in batches] == [2, 2, 1]

    def test_process_summary(self) -> None:
        processor = BatchProcessor()
        documents = [DocumentRecord(title="A", content="a"), DocumentRecord(title="B", content="b")]

        def processor_fn(document: DocumentRecord) -> str:
            return f"doc-{document.title}"

        summary = processor.process(documents, processor_fn)
        assert summary["total"] == 2
        assert summary["succeeded"] == 2
        assert summary["failed"] == 0
        assert len(summary["results"]) == 2

    def test_process_failures(self) -> None:
        processor = BatchProcessor()

        def processor_fn(document: DocumentRecord) -> str:
            raise ValueError("boom")

        summary = processor.process([DocumentRecord(title="A", content="a")], processor_fn)
        assert summary["failed"] == 1
        assert summary["results"][0]["status"] == "failed"


class TestIngestionEngine:
    def test_ingest_document(self) -> None:
        engine = IngestionEngine()
        document = DocumentRecord(title="Manual", content="Conteudo do manual para ingestao completa.")
        result = engine.ingest_document(document)
        assert result["document_id"] == "doc-1"
        assert result["chunks"] == 1
        assert result["embeddings"] == 1

    def test_ingest_batch(self) -> None:
        engine = IngestionEngine()
        documents = [DocumentRecord(title=f"D{index}", content=f"Conteudo do documento {index}.") for index in range(3)]
        summary = engine.ingest_batch(documents)
        assert summary["total"] == 3
        assert summary["succeeded"] == 3
        assert summary["failed"] == 0

    def test_stats(self) -> None:
        engine = IngestionEngine()
        engine.ingest_document(DocumentRecord(title="T", content="Conteudo para a estatistica do motor."))
        stats = engine.stats()
        assert stats["documents"] == 1
        assert stats["vectors"] == 1
        assert stats["tracker"]["done"] == 1
