"""
Confidentiality Manager - Control confidential document access.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from ..legal_config import LegalConfig

logger = logging.getLogger(__name__)


class ConfidentialityManager:
    def __init__(self, config: LegalConfig):
        self.config = config
        self._classified_docs: Dict[str, str] = {}
        self._clearance: Dict[str, Set[str]] = {}

    def classify(self, document_id: str, level: str) -> None:
        self._classified_docs[document_id] = level

    def grant_clearance(self, user_id: str, level: str) -> None:
        if user_id not in self._clearance:
            self._clearance[user_id] = set()
        self._clearance[user_id].add(level)

    def can_access(self, user_id: str, document_id: str) -> bool:
        doc_level = self._classified_docs.get(document_id)
        if not doc_level:
            return True
        return doc_level in self._clearance.get(user_id, set())
