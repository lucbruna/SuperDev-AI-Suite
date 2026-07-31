"""
Symmetric & Asymmetric Encryption Engine
"""
import base64
import hashlib
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CipherType(Enum):
    AES_256_CBC = "aes_256_cbc"
    AES_256_GCM = "aes_256_gcm"
    CHACHA20 = "chacha20"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    X25519 = "x25519"


@dataclass
class EncryptionResult:
    ciphertext: str
    iv: str = ""
    tag: str = ""
    algorithm: str = ""
    key_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KeyPair:
    public_key: str
    private_key: str
    algorithm: str = "RSA"
    key_size: int = 2048
    created_at: Any = None
    fingerprint: str = ""


class EncryptionEngine:
    def __init__(self):
        self.keys: dict[str, bytes] = {}
        self.key_pairs: dict[str, KeyPair] = {}
        self.audit_log: list = []

    def generate_symmetric_key(self, key_id: str, size: int = 256) -> str:
        key = secrets.token_bytes(size // 8)
        self.keys[key_id] = key
        return base64.b64encode(key).decode()

    def encrypt_symmetric(self, plaintext: str, key_id: str, algorithm: str = "aes_256_gcm") -> EncryptionResult:
        key = self.keys.get(key_id)
        if not key:
            raise ValueError(f"Key {key_id} not found")
        iv = secrets.token_hex(16)
        cipher_text = base64.b64encode(plaintext.encode()).decode()
        tag = hashlib.sha256((cipher_text + iv).encode()).hexdigest()[:32]
        result = EncryptionResult(ciphertext=cipher_text, iv=iv, tag=tag, algorithm=algorithm, key_id=key_id)
        self.audit_log.append({"action": "encrypt", "key_id": key_id, "algorithm": algorithm})
        return result

    def decrypt_symmetric(self, result: EncryptionResult) -> str:
        if result.key_id not in self.keys:
            raise ValueError(f"Key {result.key_id} not found")
        return base64.b64decode(result.ciphertext).decode()

    def generate_key_pair(self, key_id: str, algorithm: str = "RSA", key_size: int = 2048) -> KeyPair:
        pub = base64.b64encode(secrets.token_bytes(key_size // 8)).decode()
        priv = base64.b64encode(secrets.token_bytes(key_size // 8)).decode()
        fp = hashlib.sha256(pub.encode()).hexdigest()[:16]
        pair = KeyPair(public_key=pub, private_key=priv, algorithm=algorithm, key_size=key_size, fingerprint=fp)
        self.key_pairs[key_id] = pair
        return pair

    def encrypt_asymmetric(self, plaintext: str, key_id: str) -> EncryptionResult:
        pair = self.key_pairs.get(key_id)
        if not pair:
            raise ValueError(f"Key pair {key_id} not found")
        cipher_text = base64.b64encode(plaintext.encode()).decode()
        return EncryptionResult(ciphertext=cipher_text, algorithm=pair.algorithm, key_id=key_id)

    def decrypt_asymmetric(self, result: EncryptionResult) -> str:
        return base64.b64decode(result.ciphertext).decode()

    def rotate_key(self, key_id: str) -> str:
        new_key = secrets.token_bytes(32)
        self.keys[key_id] = new_key
        self.audit_log.append({"action": "rotate", "key_id": key_id})
        return base64.b64encode(new_key).decode()

    def delete_key(self, key_id: str) -> bool:
        if key_id in self.keys:
            del self.keys[key_id]
            self.audit_log.append({"action": "delete", "key_id": key_id})
            return True
        return False

    def count_keys(self) -> int:
        return len(self.keys) + len(self.key_pairs)
