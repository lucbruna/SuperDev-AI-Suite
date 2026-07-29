"""
Document Encryption - Encryption services for legal documents.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Optional

from ..legal_config import LegalConfig

logger = logging.getLogger(__name__)


class DocumentEncryption:
    def __init__(self, config: LegalConfig):
        self.config = config

    def hash_document(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self, content: str, expected_hash: str) -> bool:
        return self.hash_document(content) == expected_hash
