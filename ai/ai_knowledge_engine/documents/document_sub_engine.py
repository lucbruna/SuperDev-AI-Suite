"""Document subsystem engine — Intelligent document processing and analysis."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DocumentType(Enum):
    PDF = "pdf"
    TEXT = "text"
    MARKDOWN = "markdown"
    CODE = "code"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"


class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessedDocument:
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    content: str = ""
    doc_type: DocumentType = DocumentType.TEXT
    chunks: list[str] = field(default_factory=list)
    summary: str = ""
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: ProcessingStatus = ProcessingStatus.PENDING
    processed_at: datetime | None = None


@dataclass
class ExtractionResult:
    result_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    doc_id: str = ""
    field_name: str = ""
    value: str = ""
    confidence: float = 0.0
    context: str = ""


class DocumentSubEngine:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self._documents: dict[str, ProcessedDocument] = {}
        self._extractions: list[ExtractionResult] = []
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._templates: dict[str, list[str]] = {}

    def process_document(self, title: str, content: str, doc_type: str = "text") -> ProcessedDocument:
        dt = DocumentType(doc_type) if doc_type in [e.value for e in DocumentType] else DocumentType.TEXT
        chunks = self._chunk_text(content)
        doc = ProcessedDocument(
            title=title,
            content=content,
            doc_type=dt,
            chunks=chunks,
            keywords=self._extract_keywords(content),
            status=ProcessingStatus.COMPLETED,
            processed_at=datetime.now(),
        )
        self._documents[doc.doc_id] = doc
        return doc

    def get_document(self, doc_id: str) -> ProcessedDocument | None:
        return self._documents.get(doc_id)

    def summarize(self, doc_id: str) -> str:
        doc = self._documents.get(doc_id)
        if not doc:
            return ""
        sentences = doc.content.split(". ")
        doc.summary = ". ".join(sentences[:3]) + "." if len(sentences) > 3 else doc.content
        return doc.summary

    def extract_information(self, doc_id: str, fields: list[str]) -> list[ExtractionResult]:
        doc = self._documents.get(doc_id)
        if not doc:
            return []
        results = []
        for field_name in fields:
            value = doc.metadata.get(field_name, "")
            if not value and field_name.lower() in doc.content.lower():
                idx = doc.content.lower().index(field_name.lower())
                value = doc.content[max(0, idx-50):idx+100]
            result = ExtractionResult(
                doc_id=doc_id,
                field_name=field_name,
                value=value,
                confidence=0.7 if value else 0.0,
            )
            results.append(result)
            self._extractions.append(result)
        return results

    def search_documents(self, query: str) -> list[ProcessedDocument]:
        query_lower = query.lower()
        return [d for d in self._documents.values() if query_lower in d.title.lower() or query_lower in d.content.lower()]

    def add_template(self, name: str, fields: list[str]) -> None:
        self._templates[name] = fields

    def get_template(self, name: str) -> list[str] | None:
        return self._templates.get(name)

    def _chunk_text(self, text: str) -> list[str]:
        chunks = []
        for i in range(0, len(text), self._chunk_size - self._chunk_overlap):
            chunk = text[i:i + self._chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks

    def _extract_keywords(self, text: str) -> list[str]:
        words = text.lower().split()
        word_freq = {}
        for w in words:
            if len(w) > 3:
                word_freq[w] = word_freq.get(w, 0) + 1
        return sorted(word_freq.keys(), key=lambda w: word_freq[w], reverse=True)[:10]

    def get_stats(self) -> dict:
        return {
            "total_documents": len(self._documents),
            "total_extractions": len(self._extractions),
            "completed": len([d for d in self._documents.values() if d.status == ProcessingStatus.COMPLETED]),
            "templates": len(self._templates),
        }
