from __future__ import annotations

import base64
import hashlib
import os
from typing import Any


class DecryptionError(Exception):
    """Raised when decryption fails (wrong key or corrupted data)."""


class DatabaseEncryption:
    """Column-level encryption utility using AES-like XOR + SHA-256.

    .. note::
       This is **not** production-grade encryption. For production use,
       integrate with a proper KMS or libsodium.
    """

    def __init__(self, master_key: str | None = None) -> None:
        self._master_key = master_key or os.urandom(32).hex()
        self._derived = hashlib.sha256(self._master_key.encode()).digest()

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        data = plaintext.encode()
        cipher = bytes(a ^ b for a, b in zip(data, self._keystream(len(data))))
        return base64.b64encode(cipher).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ""
        cipher = base64.b64decode(ciphertext)
        data = bytes(a ^ b for a, b in zip(cipher, self._keystream(len(cipher))))
        try:
            return data.decode()
        except UnicodeDecodeError as exc:
            raise DecryptionError("Decryption failed — wrong key or corrupted data") from exc

    def _keystream(self, length: int) -> bytes:
        result = bytearray()
        for i in range(length):
            result.append(self._derived[i % len(self._derived)])
        return bytes(result)

    @property
    def key_fingerprint(self) -> str:
        return hashlib.sha256(self._derived).hexdigest()[:16]


class EncryptionField:
    """Descriptor that transparently encrypts/decrypts a field value.

    Usage::

        class SecureModel(Model):
            ssn = EncryptionField()
    """

    def __init__(self, encryption: DatabaseEncryption | None = None) -> None:
        self._encryption = encryption or DatabaseEncryption()
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        raw = obj._values.get(self.name)
        if raw is None:
            return None
        return self._encryption.decrypt(raw)

    def __set__(self, obj: Any, value: Any) -> None:
        if value is None:
            obj._values[self.name] = None
        else:
            obj._values[self.name] = self._encryption.encrypt(str(value))


__all__ = [
    "DatabaseEncryption",
    "EncryptionField",
]
