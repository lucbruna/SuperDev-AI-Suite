"""Documents AI - Legal document management and classification."""

from .legal_document_engine import LegalDocumentEngine
from .document_classifier import DocumentClassifier
from .document_search import DocumentSearch
from .document_summary import DocumentSummary
from .archive_manager import ArchiveManager

__all__ = ["LegalDocumentEngine", "DocumentClassifier", "DocumentSearch", "DocumentSummary", "ArchiveManager"]
