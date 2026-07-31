from __future__ import annotations

import logging


class BackupEncryption:
    """Encrypts and decrypts backup data."""

    def __init__(self, key: str | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.backup.encryption")
        self._key = key

    def encrypt(self, data: bytes) -> bytes:
        raise NotImplementedError

    def decrypt(self, data: bytes) -> bytes:
        raise NotImplementedError

    def rotate_key(self, new_key: str) -> bool:
        raise NotImplementedError

    def generate_key(self) -> str:
        raise NotImplementedError
