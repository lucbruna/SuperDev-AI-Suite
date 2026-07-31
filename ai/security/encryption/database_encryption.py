"""Database encryption."""
from __future__ import annotations

import base64
import secrets
from typing import Any


class DatabaseEncryption:
    def __init__(self) -> None:
        self._column_keys: dict[str, bytes] = {}
        self._encrypted_tables: dict[str, dict[str, Any]] = {}
    def generate_column_key(self, table: str, column: str) -> str:
        key_id = f"{table}.{column}"
        self._column_keys[key_id] = secrets.token_bytes(32)
        return key_id
    def encrypt_column_value(self, table: str, column: str, value: str) -> str:
        key_id = f"{table}.{column}"
        key = self._column_keys.get(key_id)
        if not key:
            key = secrets.token_bytes(32)
            self._column_keys[key_id] = key
        data_bytes = value.encode()
        key_expanded = (key * ((len(data_bytes) // 32) + 1))[:len(data_bytes)]
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_expanded, strict=False))
        return base64.b64encode(encrypted).decode()
    def decrypt_column_value(self, table: str, column: str, ciphertext: str) -> str | None:
        key_id = f"{table}.{column}"
        key = self._column_keys.get(key_id)
        if not key:
            return None
        encrypted = base64.b64decode(ciphertext)
        key_expanded = (key * ((len(encrypted) // 32) + 1))[:len(encrypted)]
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_expanded, strict=False))
        return decrypted.decode()
    def encrypt_row(self, table: str, row: dict[str, str]) -> dict[str, str]:
        return {col: self.encrypt_column_value(table, col, val) for col, val in row.items()}
    def decrypt_row(self, table: str, row: dict[str, str]) -> dict[str, str | None]:
        return {col: self.decrypt_column_value(table, col, val) for col, val in row.items()}
    def list_encrypted_columns(self) -> list[str]:
        return list(self._column_keys.keys())
