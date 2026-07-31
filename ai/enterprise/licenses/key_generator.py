"""License key generator."""
from __future__ import annotations
import random, string

class LicenseKeyGenerator:
    def __init__(self, prefix: str = "SD", length: int = 32) -> None:
        self._prefix = prefix
        self._length = length
        self._generated: list = []
    def generate(self) -> str:
        chars = string.ascii_uppercase + string.digits
        key_body = ''.join(random.choices(chars, k=self._length))
        key = f"{self._prefix}-{key_body[:8]}-{key_body[8:16]}-{key_body[16:24]}-{key_body[24:]}"
        self._generated.append(key)
        return key
    def generate_batch(self, count: int) -> list:
        return [self.generate() for _ in range(count)]
    def is_valid_format(self, key: str) -> bool:
        parts = key.split('-')
        return len(parts) == 5 and parts[0] == self._prefix
    def get_generated_count(self) -> int:
        return len(self._generated)
    def list_keys(self) -> list:
        return list(self._generated)
