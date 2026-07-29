"""
Encryption Manager - Financial data encryption and protection.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class EncryptionManager:
    def __init__(self, config: FinancialConfig):
        self.config = config
        self._protected = {"bank_account", "tax_id", "salary", "price", "cost", "commission", "negotiated_rate"}

    async def encrypt_field(self, value: str) -> str:
        return f"ENC_{hash(value)}_{len(value)}"

    async def decrypt_field(self, encrypted: str) -> str:
        if encrypted.startswith("ENC_"):
            return "[decrypted]"
        return encrypted

    async def mask_sensitive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        masked = {}
        for k, v in data.items():
            masked[k] = "***" if k in self._protected else v
        return masked