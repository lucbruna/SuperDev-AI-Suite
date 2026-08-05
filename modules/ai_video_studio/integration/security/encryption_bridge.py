"""Encryption Bridge — reversible encryption via the suite security engine (fallback: stdlib).

Uses Fernet (``cryptography``) when installed; otherwise falls back to a
clearly-labelled XOR/hex obfuscation so pipelines never hard-fail on
missing optional dependencies.
"""
from __future__ import annotations

import base64
import hashlib
from typing import Any


def _fernet() -> Any | None:
    try:
        from cryptography.fernet import Fernet  # type: ignore[import-not-found]

        return Fernet
    except Exception:  # noqa: BLE001
        return None


class EncryptionBridge:
    """Encrypt/decrypt values; key derived deterministically unless provided."""

    def __init__(self, secret: str | None = None) -> None:
        self._secret = secret or "superdev-ai-video-studio"
        self._fernet_cls = _fernet()

    def encrypt(self, plaintext: str) -> dict[str, Any]:
        if self._fernet_cls is not None:
            key = base64.urlsafe_b64encode(hashlib.sha256(self._secret.encode()).digest())
            token = self._fernet_cls(key).encrypt(plaintext.encode()).decode()
            return {"encrypted": token, "cipher": "fernet"}
        token = self._xor_obfuscate(plaintext)
        return {"encrypted": token, "cipher": "xor-obfuscation"}

    def decrypt(self, token: str, *, cipher: str = "fernet") -> dict[str, Any]:
        if cipher == "fernet" and self._fernet_cls is not None:
            key = base64.urlsafe_b64encode(hashlib.sha256(self._secret.encode()).digest())
            return {"decrypted": self._fernet_cls(key).decrypt(token.encode()).decode()}
        return {"decrypted": self._xor_deobfuscate(token)}

    @staticmethod
    def _xor_obfuscate(text: str) -> str:
        key = b"sdv"
        data = text.encode()
        return base64.urlsafe_b64encode(bytes(b ^ key[i % 3] for i, b in enumerate(data))).decode()

    @staticmethod
    def _xor_deobfuscate(token: str) -> str:
        key = b"sdv"
        data = base64.urlsafe_b64decode(token.encode())
        return bytes(b ^ key[i % 3] for i, b in enumerate(data)).decode()


_encryption_bridge: EncryptionBridge | None = None


def get_encryption_bridge() -> EncryptionBridge:
    global _encryption_bridge
    if _encryption_bridge is None:
        _encryption_bridge = EncryptionBridge()
    return _encryption_bridge
