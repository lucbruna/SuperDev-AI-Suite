"""
Privacy Manager - Protect customer personally identifiable information.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class PrivacyManager:
    def __init__(self, config: CustomerConfig):
        self.config = config
        self._pii_patterns = {
            "email": r'[\w\.-]+@[\w\.-]+\.\w+',
            "phone": r'\+?\d[\d\s\-\(\)]{7,}\d',
            "cpf": r'\d{3}\.\d{3}\.\d{3}-\d{2}',
            "credit_card": r'\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}',
        }

    def mask_email(self, email: str) -> str:
        parts = email.split("@")
        if len(parts) != 2:
            return email
        name_part = parts[0]
        masked = name_part[0] + "***" + name_part[-1] if len(name_part) > 2 else name_part[0] + "***"
        return masked + "@" + parts[1]

    def mask_phone(self, phone: str) -> str:
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 10:
            return digits[:2] + "****" + digits[-4:]
        return "****"

    def mask_cpf(self, cpf: str) -> str:
        digits = re.sub(r'\D', '', cpf)
        if len(digits) == 11:
            return "***." + digits[3:6] + ".***-**"
        return "***.***.***-**"

    def anonymize(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in profile.items():
            if k == "email" and isinstance(v, str):
                result[k] = self.mask_email(v)
            elif k == "phone" and isinstance(v, str):
                result[k] = self.mask_phone(v)
            elif k == "cpf" and isinstance(v, str):
                result[k] = self.mask_cpf(v)
            elif k in ("name", "full_name") and isinstance(v, str):
                parts = v.split()
                result[k] = parts[0] + " " + " ".join(p[0] + "." for p in parts[1:]) if len(parts) > 1 else parts[0]
            else:
                result[k] = v
        return result

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        found = {}
        for pii_type, pattern in self._pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                found[pii_type] = matches
        return found

    def strip_pii(self, text: str) -> str:
        result = text
        for pii_type, pattern in self._pii_patterns.items():
            result = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", result)
        return result
