"""Document management subsystem (Volume 27, Fase 4)."""

from __future__ import annotations

from .classification import DocumentClassifier
from .document_engine import DocumentEngine
from .document_manager import DocumentManager
from .extractor import EntityExtractor
from .metadata import MetadataExtractor
from .parser import DocumentParser

__all__ = [
    "DocumentClassifier",
    "DocumentEngine",
    "DocumentManager",
    "DocumentParser",
    "EntityExtractor",
    "MetadataExtractor",
]
