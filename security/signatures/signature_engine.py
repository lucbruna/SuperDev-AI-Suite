"""Signatures subsystem (Volume 16) — HMAC signing and verification.

Demonstração stdlib (HMAC-SHA256). Para assinaturas assimétricas reais,
substitua por uma lib auditada (cryptography/ed25519).
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any

from ..security_models import SignatureAlgorithm, SignatureResult


class SignatureEngine:
    """Sign and verify payloads with HMAC-SHA256 keys."""

    name = "signatures"
    description = "HMAC signing and verification"

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._signing_key: bytes | None = None

    def generate_key(self, size: int = 32) -> bytes:
        key = os.urandom(size)
        self._signing_key = key
        return key

    def sign(self, payload: str | bytes, key: bytes | None = None) -> SignatureResult:
        key = key if key is not None else (self._signing_key or self.generate_key())
        raw = payload.encode("utf-8") if isinstance(payload, str) else payload
        signature = hmac.new(key, raw, hashlib.sha256).hexdigest()
        if self.engine is not None:
            self.engine.metrics.increment("security.signatures")
        return SignatureResult(
            signature=signature,
            algorithm=SignatureAlgorithm.ED25519.value,
            public_key=hashlib.sha256(key).hexdigest()[:16],
        )

    def verify(self, payload: str | bytes, signature: str, key: bytes) -> SignatureResult:
        expected = self.sign(payload, key)
        valid = hmac.compare_digest(expected.signature, signature)
        if self.engine is not None:
            self.engine.metrics.increment("security.signature_verifications")
        return SignatureResult(
            signature=signature,
            algorithm=expected.algorithm,
            public_key=expected.public_key,
            valid=valid,
        )

    def sign_and_verify(self, payload: str) -> SignatureResult:
        signed = self.sign(payload)
        return self.verify(payload, signed.signature, self._signing_key or b"")

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._signing_key is not None,
            "algorithm": "hmac-sha256",
            "key_id": hashlib.sha256(self._signing_key).hexdigest()[:16]
            if self._signing_key
            else None,
        }


__all__ = ["SignatureEngine"]
