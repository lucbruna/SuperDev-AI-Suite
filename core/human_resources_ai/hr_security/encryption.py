"""
Encryption Manager - Encryption services for HR data.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Optional

from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class EncryptionManager:
    def __init__(self, config: HRConfig):
        self.config = config

    def hash_value(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def obfuscate_salary(self, salary: float) -> str:
        return f"***{int(salary) % 10000:04d}"
