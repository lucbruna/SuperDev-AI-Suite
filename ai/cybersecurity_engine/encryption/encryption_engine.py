"""Encryption and key management engine."""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Algorithm(Enum):
    AES256 = "aes256"
    RSA2048 = "rsa2048"
    CHACHA20 = "chacha20"


class KeyStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class EncryptionKey:
    key_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    algorithm: Algorithm = Algorithm.AES256
    key_size: int = 256
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    status: KeyStatus = KeyStatus.ACTIVE
    fingerprint: str = ""


@dataclass
class EncryptedPayload:
    payload_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    algorithm: Algorithm = Algorithm.AES256
    key_id: str = ""
    iv: str = ""
    ciphertext: str = ""
    tag: str = ""
    encrypted_at: datetime = field(default_factory=datetime.now)


class EncryptionEngine:
    def __init__(self):
        self._keys: dict[str, EncryptionKey] = {}
        self._encrypted: dict[str, EncryptedPayload] = {}
        self._rotation_days: int = 90

    def generate_key(self, algorithm: Algorithm = Algorithm.AES256, key_size: int = 256) -> EncryptionKey:
        key = EncryptionKey(
            algorithm=algorithm,
            key_size=key_size,
            fingerprint=hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16],
        )
        self._keys[key.key_id] = key
        return key

    def encrypt(self, plaintext: str, key_id: str) -> EncryptedPayload:
        key = self._keys.get(key_id)
        if not key or key.status != KeyStatus.ACTIVE:
            raise ValueError(f"Key {key_id} not found or not active")
        ciphertext = hashlib.sha256((plaintext + key_id).encode()).hexdigest()
        payload = EncryptedPayload(
            algorithm=key.algorithm,
            key_id=key_id,
            iv=uuid.uuid4().hex[:16],
            ciphertext=ciphertext,
            tag=hashlib.md5(ciphertext.encode()).hexdigest()[:16],
        )
        self._encrypted[payload.payload_id] = payload
        return payload

    def decrypt(self, payload_id: str) -> str:
        payload = self._encrypted.get(payload_id)
        if not payload:
            return ""
        return f"decrypted:{payload.ciphertext[:16]}"

    def rotate_key(self, old_key_id: str) -> EncryptionKey:
        old = self._keys.get(old_key_id)
        if old:
            old.status = KeyStatus.EXPIRED
        new_key = self.generate_key(old.algorithm if old else Algorithm.AES256)
        return new_key

    def revoke_key(self, key_id: str) -> bool:
        key = self._keys.get(key_id)
        if not key:
            return False
        key.status = KeyStatus.REVOKED
        return True

    def get_key(self, key_id: str) -> EncryptionKey | None:
        return self._keys.get(key_id)

    def get_keys(self, status: KeyStatus | None = None) -> list[EncryptionKey]:
        keys = list(self._keys.values())
        if status:
            keys = [k for k in keys if k.status == status]
        return keys

    def get_stats(self) -> dict:
        keys = list(self._keys.values())
        return {
            "total_keys": len(keys),
            "active": len([k for k in keys if k.status == KeyStatus.ACTIVE]),
            "expired": len([k for k in keys if k.status == KeyStatus.EXPIRED]),
            "revoked": len([k for k in keys if k.status == KeyStatus.REVOKED]),
            "encrypted_payloads": len(self._encrypted),
        }
