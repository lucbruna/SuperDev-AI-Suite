"""Data encryption at rest."""
from __future__ import annotations
from typing import Any, Dict, Optional
import hashlib, base64, secrets

class DataEncryption:
    def __init__(self) -> None:
        self._master_key = secrets.token_bytes(32)
        self._encrypted_store: Dict[str, str] = {}
    def encrypt_field(self, field_id: str, value: str) -> str:
        data_bytes = value.encode()
        key_expanded = (self._master_key * ((len(data_bytes) // 32) + 1))[:len(data_bytes)]
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_expanded))
        encoded = base64.b64encode(encrypted).decode()
        self._encrypted_store[field_id] = encoded
        return encoded
    def decrypt_field(self, field_id: str) -> Optional[str]:
        encoded = self._encrypted_store.get(field_id)
        if not encoded:
            return None
        encrypted = base64.b64decode(encoded)
        key_expanded = (self._master_key * ((len(encrypted) // 32) + 1))[:len(encrypted)]
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_expanded))
        return decrypted.decode()
    def encrypt_fields(self, fields: Dict[str, str]) -> Dict[str, str]:
        return {k: self.encrypt_field(k, v) for k, v in fields.items()}
    def decrypt_fields(self, field_ids: list[str]) -> Dict[str, Optional[str]]:
        return {fid: self.decrypt_field(fid) for fid in field_ids}
    def delete_field(self, field_id: str) -> bool:
        if field_id in self._encrypted_store:
            del self._encrypted_store[field_id]
            return True
        return False
    def hash_value(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()
    def mask(self, value: str, visible: int = 4) -> str:
        if len(value) <= visible:
            return "*" * len(value)
        return value[:visible] + "*" * (len(value) - visible)
