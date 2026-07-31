"""Encryption engine."""
from __future__ import annotations
from typing import Any, Dict, Optional
from enum import Enum
import hashlib, base64, secrets

class EncryptionAlgorithm(Enum):
    AES256 = "aes256"
    RSA = "rsa"
    CHACHA20 = "chacha20"

class EncryptionEngine:
    def __init__(self) -> None:
        self._keys: Dict[str, bytes] = {}
        self._algorithm = EncryptionAlgorithm.AES256
    def generate_key(self, key_id: str, size: int = 32) -> str:
        key = secrets.token_bytes(size)
        self._keys[key_id] = key
        return key_id
    def encrypt(self, data: str, key_id: str) -> Dict[str, Any]:
        key = self._keys.get(key_id)
        if not key:
            return {"error": "key_not_found"}
        data_bytes = data.encode()
        key_expanded = (key * ((len(data_bytes) // len(key)) + 1))[:len(data_bytes)]
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, key_expanded))
        return {"ciphertext": base64.b64encode(encrypted).decode(), "key_id": key_id, "algorithm": self._algorithm.value}
    def decrypt(self, ciphertext: str, key_id: str) -> Dict[str, Any]:
        key = self._keys.get(key_id)
        if not key:
            return {"error": "key_not_found"}
        try:
            encrypted = base64.b64decode(ciphertext)
            key_expanded = (key * ((len(encrypted) // len(key)) + 1))[:len(encrypted)]
            decrypted = bytes(a ^ b for a, b in zip(encrypted, key_expanded))
            return {"plaintext": decrypted.decode(), "key_id": key_id}
        except Exception as e:
            return {"error": str(e)}
    def rotate_key(self, old_key_id: str, new_key_id: str) -> bool:
        if old_key_id in self._keys:
            self.generate_key(new_key_id)
            return True
        return False
    def delete_key(self, key_id: str) -> bool:
        if key_id in self._keys:
            del self._keys[key_id]
            return True
        return False
    def list_keys(self) -> list[str]:
        return list(self._keys.keys())
