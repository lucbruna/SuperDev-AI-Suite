from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Any

from .database_logger import DatabaseLogger


class DatabaseSecurity:
    """Credential management, encryption key handling, and secure configuration."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._logger = logger or DatabaseLogger("database.security")
        self._encryption_key: bytes | None = None
        self._master_key: bytes | None = None

    def set_encryption_key(self, key: bytes | str) -> None:
        if isinstance(key, str):
            key = key.encode("utf-8")
        self._encryption_key = hashlib.sha256(key).digest()
        self._logger.info("Encryption key configured")

    def set_master_key(self, key: bytes | str) -> None:
        if isinstance(key, str):
            key = key.encode("utf-8")
        self._master_key = hashlib.sha256(key).digest()

    def encrypt_password(self, password: str) -> str:
        if not self._encryption_key:
            self._logger.warning("No encryption key set, using base64 encoding only")
            return base64.b64encode(password.encode()).decode()
        iv = os.urandom(16)
        from hashlib import pbkdf2_hmac

        derived = pbkdf2_hmac("sha256", self._encryption_key, iv, 100000, dklen=32)
        encrypted = bytes(a ^ b for a, b in zip(password.encode().ljust(64, b"\0")[:64], derived))
        return base64.b64encode(iv + encrypted).decode()

    def decrypt_password(self, encrypted: str) -> str:
        if not self._encryption_key:
            try:
                return base64.b64decode(encrypted).decode().rstrip("\x00")
            except Exception:
                return encrypted
        raw = base64.b64decode(encrypted)
        iv = raw[:16]
        cipher = raw[16:]
        from hashlib import pbkdf2_hmac

        derived = pbkdf2_hmac("sha256", self._encryption_key, iv, 100000, dklen=32)
        decrypted = bytes(a ^ b for a, b in zip(cipher, derived)).rstrip(b"\x00").decode(errors="replace")
        return decrypted

    def mask_credentials(self, dsn: str) -> str:
        result = dsn
        for field in ("password", "passwd", "pwd"):
            marker = f"{field}="
            if marker in result:
                start = result.index(marker) + len(marker)
                end = result.index(" ", start) if " " in result[start:] else len(result)
                result = result[:start] + "****" + result[end:]
        return result

    def generate_connection_secret(self) -> str:
        return secrets.token_urlsafe(32)

    def validate_ssl_config(self, ssl: bool, host: str) -> bool:
        if ssl and host in ("localhost", "127.0.0.1", "::1"):
            self._logger.warning(f"SSL enabled for localhost connection to {host}")
        return True
