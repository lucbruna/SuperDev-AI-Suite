"""Database encryption."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import hashlib, base64, secrets

class DatabaseEncryption:
    def __init__(self) -> None:
        self._column_keys: Dict[str, bytes] = {}
        self._encrypted_tables: Dict[str, Dict[str, Any]] = {}
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
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_expanded))
        return base64.b64encode(encrypted).decode()
    def decrypt_column_value(self, table: str, column: str, ciphertext: str) -> Optional[str]:
        key_id = f"{table}.{column}"
        key = self._column_keys.get(key_id)
        if not key:
            return None
        encrypted = base64.b64decode(ciphertext)
        key_expanded = (key * ((len(encrypted) // 32) + 1))[:len(encrypted)]
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_expanded))
        return decrypted.decode()
    def encrypt_row(self, table: str, row: Dict[str, str]) -> Dict[str, str]:
        return {col: self.encrypt_column_value(table, col, val) for col, val in row.items()}
    def decrypt_row(self, table: str, row: Dict[str, str]) -> Dict[str, Optional[str]]:
        return {col: self.decrypt_column_value(table, col, val) for col, val in row.items()}
    def list_encrypted_columns(self) -> list[str]:
        return list(self._column_keys.keys())
