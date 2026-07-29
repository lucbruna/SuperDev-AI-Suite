"""
Document Classifier - Classify legal documents by type and category.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..legal_context import LegalContext
from ..legal_events import LegalEventBus
from ..legal_models import LegalDocument, DocumentType
from ..legal_config import LegalConfig

logger = logging.getLogger(__name__)


class DocumentClassifier:
    def __init__(self, config: LegalConfig, context: LegalContext, event_bus: LegalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    def classify(self, doc: LegalDocument) -> DocumentType:
        title_lower = doc.title.lower()
        if "contract" in title_lower or "agreement" in title_lower:
            return DocumentType.CONTRACT
        if "opinion" in title_lower or "parecer" in title_lower:
            return DocumentType.OPINION
        if "license" in title_lower or "licen" in title_lower:
            return DocumentType.LICENSE
        if "certificate" in title_lower or "certid" in title_lower:
            return DocumentType.CERTIFICATE
        if "policy" in title_lower or "política" in title_lower:
            return DocumentType.POLICY
        if "report" in title_lower or "relatório" in title_lower:
            return DocumentType.REPORT
        return DocumentType.CONTRACT

    def suggest_tags(self, doc: LegalDocument) -> List[str]:
        return ["legal", doc.document_type.value, doc.department]
