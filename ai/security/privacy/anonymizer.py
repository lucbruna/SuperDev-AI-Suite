"""Data anonymization."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any


class AnonymizationMethod:
    HASH = "hash"
    MASK = "mask"
    REMOVE = "remove"
    GENERALIZE = "generalize"
    PERTURB = "perturb"
    K_ANONYMITY = "k_anonymity"


class DataAnonymizer:
    def __init__(self) -> None:
        self._transformations: list[dict[str, Any]] = []
        self._salt = uuid.uuid4().hex[:16]

    def hash_value(self, value: str) -> str:
        return hashlib.sha256((value + self._salt).encode()).hexdigest()[:16]

    def mask_value(self, value: str, visible_start: int = 2, visible_end: int = 2, mask_char: str = "*") -> str:
        if len(value) <= visible_start + visible_end:
            return mask_char * len(value)
        masked_len = len(value) - visible_start - visible_end
        return value[:visible_start] + mask_char * masked_len + value[-visible_end:]

    def generalize_age(self, age: int, bucket_size: int = 10) -> str:
        lower = (age // bucket_size) * bucket_size
        return f"{lower}-{lower + bucket_size - 1}"

    def generalize_location(self, location: str, level: str = "city") -> str:
        parts = location.split(",")
        if level == "country" and len(parts) > 1:
            return parts[-1].strip()
        if level == "state" and len(parts) > 1:
            return ",".join(parts[-2:]).strip()
        return location

    def perturb_value(self, value: float, max_delta: float = 0.1) -> float:
        import random

        delta = random.uniform(-max_delta, max_delta)
        return value + delta

    def anonymize_record(self, record: dict[str, Any], rules: dict[str, str]) -> dict[str, Any]:
        result = {}
        for key, value in record.items():
            method = rules.get(key, "none")
            if method == AnonymizationMethod.HASH:
                result[key] = self.hash_value(str(value))
            elif method == AnonymizationMethod.MASK:
                result[key] = self.mask_value(str(value))
            elif method == AnonymizationMethod.REMOVE:
                result[key] = "[REDACTED]"
            elif method == AnonymizationMethod.GENERALIZE and isinstance(value, int):
                result[key] = self.generalize_age(value)
            elif method == AnonymizationMethod.PERTURB and isinstance(value, (int, float)):
                result[key] = self.perturb_value(float(value))
            else:
                result[key] = value
        self._transformations.append({"record_keys": list(record.keys()), "methods": rules})
        return result

    def get_transformations(self) -> list[dict[str, Any]]:
        return list(self._transformations)
