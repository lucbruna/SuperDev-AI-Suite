from __future__ import annotations

import base64
import hashlib
import os
from typing import Any


class VectorEncryption:
    """Encrypt and decrypt vector data at rest."""

    def __init__(self, key: bytes | None = None):
        if key is None:
            key = hashlib.sha256(b"default-key-change-in-production").digest()
        self.key = key

    def encrypt_vector(self, vector: list[float]) -> str:
        """Simple XOR-based obfuscation (not production-grade)."""
        data = ",".join(str(v) for v in vector).encode()
        key_bytes = self.key[: len(data)].ljust(len(data), b"\x00") if len(self.key) < len(data) else self.key[: len(data)]
        encrypted = bytes(a ^ b for a, b in zip(data, key_bytes))
        return base64.b64encode(encrypted).decode()

    def decrypt_vector(self, encrypted: str) -> list[float]:
        raw = base64.b64decode(encrypted)
        key_bytes = self.key[: len(raw)].ljust(len(raw), b"\x00") if len(self.key) < len(raw) else self.key[: len(raw)]
        decrypted = bytes(a ^ b for a, b in zip(raw, key_bytes))
        return [float(x) for x in decrypted.decode().split(",")]

    def rotate_key(self, new_key: bytes) -> None:
        self.key = new_key
