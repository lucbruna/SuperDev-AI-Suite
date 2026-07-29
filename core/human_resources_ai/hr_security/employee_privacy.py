"""
Employee Privacy - Privacy protection for employee data.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..hr_config import HRConfig

logger = logging.getLogger(__name__)


class EmployeePrivacy:
    def __init__(self, config: HRConfig):
        self.config = config
        self._anonymized_fields = {"name", "email", "phone", "address", "tax_id", "bank_account", "health_info"}

    def anonymize(self, record: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in record.items():
            if k in self._anonymized_fields and isinstance(v, str):
                result[k] = v[:1] + "***" + v[-1:] if len(v) > 2 else "***"
            else:
                result[k] = v
        return result

    def mask_sensitive(self, value: str, visible_chars: int = 4) -> str:
        if len(value) <= visible_chars:
            return value
        return value[:visible_chars] + "*" * (len(value) - visible_chars)
