"""
Document Summary - Generate summaries of legal documents.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEventBus
from ..legal_models import LegalDocument
from ..legal_config import LegalConfig

logger = logging.getLogger(__name__)


class DocumentSummary:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def summarize(self, doc: LegalDocument, max_length: int = 200) -> str:
        return f"Summary of {doc.title}: Legal document of type {doc.document_type.value}. {len(doc.content)} characters."

    def extract_key_points(self, doc: LegalDocument) -> List[str]:
        return [
            f"Document: {doc.title}",
            f"Type: {doc.document_type.value}",
            f"Author: {doc.author}",
            f"Classification: {'Confidential' if doc.confidential else 'Public'}",
        ]
