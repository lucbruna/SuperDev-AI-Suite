"""File encryption."""
from __future__ import annotations

import base64
import hashlib
import secrets
from typing import Any


class FileEncryption:
    def __init__(self) -> None:
        self._key = secrets.token_bytes(32)
        self._encrypted_files: dict[str, dict[str, Any]] = {}
    def encrypt_content(self, file_path: str, content: bytes) -> dict[str, Any]:
        key_expanded = (self._key * ((len(content) // 32) + 1))[:len(content)]
        encrypted = bytes(a ^ b for a, b in zip(content, key_expanded, strict=False))
        encoded = base64.b64encode(encrypted).decode()
        checksum = hashlib.sha256(content).hexdigest()
        self._encrypted_files[file_path] = {"encoded": encoded, "checksum": checksum, "size": len(content)}
        return {"file_path": file_path, "checksum": checksum, "encrypted_size": len(encoded)}
    def decrypt_content(self, file_path: str) -> bytes | None:
        data = self._encrypted_files.get(file_path)
        if not data:
            return None
        encrypted = base64.b64decode(data["encoded"])
        key_expanded = (self._key * ((len(encrypted) // 32) + 1))[:len(encrypted)]
        return bytes(a ^ b for a, b in zip(encrypted, key_expanded, strict=False))
    def verify_integrity(self, file_path: str) -> bool:
        data = self._encrypted_files.get(file_path)
        if not data:
            return False
        decrypted = self.decrypt_content(file_path)
        if decrypted is None:
            return False
        return hashlib.sha256(decrypted).hexdigest() == data["checksum"]
    def list_encrypted(self) -> list[str]:
        return list(self._encrypted_files.keys())
    def delete(self, file_path: str) -> bool:
        if file_path in self._encrypted_files:
            del self._encrypted_files[file_path]
            return True
        return False
