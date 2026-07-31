"""Encryption subsystem (Volume 16) — stdlib-only symmetric encryption.

Nota: implementação educacional/demonstrativa baseada em primitivas do
stdlib (hash-based keystream + base64). Para produção, substitua por uma
lib auditada (cryptography). Mantém a mesma interface: ``encrypt`` /
``decrypt`` / ``generate_key``.
"""

from __future__ import annotations

import base64
import hashlib
import os
from typing import Any

from ..security_models import EncryptedPayload


class EncryptionEngine:
    """Symmetric encryption with a keyed hash-based keystream."""

    name = "encryption"
    description = "Encrypt/decrypt with a stdlib keystream cipher"

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._key: bytes | None = None

    def generate_key(self, size: int = 32) -> bytes:
        key = os.urandom(size)
        self._key = key
        return key

    def set_key(self, key: bytes) -> None:
        self._key = bytes(key)

    def _keystream(self, key: bytes, nonce: bytes, length: int) -> bytes:
        """Deterministic keystream derived from (key, nonce)."""
        out = bytearray()
        counter = 0
        while len(out) < length:
            out.extend(
                hashlib.sha256(key + nonce + counter.to_bytes(8, "big")).digest()
            )
            counter += 1
        return bytes(out[:length])

    def encrypt(self, plaintext: str, key: bytes | None = None) -> EncryptedPayload:
        """Encrypt plaintext and return an EncryptedPayload (nonce + ciphertext)."""
        key = key if key is not None else (self._key or self.generate_key())
        nonce = os.urandom(16)
        data = plaintext.encode("utf-8")
        keystream = self._keystream(key, nonce, len(data))
        ciphertext = bytes(a ^ b for a, b in zip(data, keystream, strict=False))
        key_id = hashlib.sha256(key).hexdigest()[:16]
        payload = EncryptedPayload(
            ciphertext=base64.b64encode(ciphertext).decode(),
            nonce=base64.b64encode(nonce).decode(),
            algorithm="stdlib-keystream",
            key_id=key_id,
        )
        if self.engine is not None:
            self.engine.metrics.increment("security.encryptions")
        return payload

    def decrypt(self, payload: EncryptedPayload | dict[str, Any], key: bytes) -> str:
        """Decrypt an EncryptedPayload (or its dict form) with the given key."""
        if isinstance(payload, dict):
            payload = EncryptedPayload(
                ciphertext=payload["ciphertext"],
                nonce=payload["nonce"],
                algorithm=payload.get("algorithm", "stdlib-keystream"),
                key_id=payload.get("key_id", ""),
            )
        ciphertext = base64.b64decode(payload.ciphertext)
        nonce = base64.b64decode(payload.nonce)
        keystream = self._keystream(key, nonce, len(ciphertext))
        if self.engine is not None:
            self.engine.metrics.increment("security.decryptions")
        # ``errors="replace"``: com a chave errada os bytes são aleatórios e
        # podem não ser UTF-8 válido — substituir evita exceção e o resultado
        # nunca coincide com o texto original (garantia do teste).
        return bytes(
            a ^ b for a, b in zip(ciphertext, keystream, strict=False)
        ).decode("utf-8", errors="replace")

    def roundtrip(self, plaintext: str, key: bytes | None = None) -> str:
        payload = self.encrypt(plaintext, key)
        return self.decrypt(payload, key if key is not None else (self._key or b""))

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._key is not None,
            "algorithm": "stdlib-keystream",
            "key_id": hashlib.sha256(self._key).hexdigest()[:16] if self._key else None,
        }


__all__ = ["EncryptionEngine"]
