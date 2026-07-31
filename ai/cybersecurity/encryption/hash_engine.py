"""
Cryptographic Hashing Engine
"""

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HashAlgorithm(Enum):
    SHA256 = "sha256"
    SHA512 = "sha512"
    SHA3_256 = "sha3_256"
    MD5 = "md5"
    HMAC_SHA256 = "hmac_sha256"


@dataclass
class HashResult:
    digest: str
    algorithm: str
    hex_digest: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class HashEngine:
    def __init__(self):
        self.salt_store: dict[str, bytes] = {}

    def hash_data(self, data: str, algorithm: str = "sha256") -> HashResult:
        if algorithm == "sha256":
            h = hashlib.sha256(data.encode())
        elif algorithm == "sha512":
            h = hashlib.sha512(data.encode())
        elif algorithm == "md5":
            h = hashlib.md5(data.encode())
        elif algorithm == "sha3_256":
            h = hashlib.sha3_256(data.encode())
        else:
            h = hashlib.sha256(data.encode())
        hex_d = h.hexdigest()
        return HashResult(digest=h.digest().hex(), algorithm=algorithm, hex_digest=hex_d)

    def hash_with_salt(self, data: str, salt_id: str, algorithm: str = "sha256") -> HashResult:
        salt = self.salt_store.get(salt_id)
        if not salt:
            salt = secrets.token_bytes(16)
            self.salt_store[salt_id] = salt
        salted = salt + data.encode()
        if algorithm == "sha256":
            h = hashlib.sha256(salted)
        elif algorithm == "sha512":
            h = hashlib.sha512(salted)
        else:
            h = hashlib.sha256(salted)
        return HashResult(digest=h.hexdigest(), algorithm=algorithm)

    def hmac_sign(self, data: str, key: str, algorithm: str = "sha256") -> HashResult:
        if algorithm == "sha256":
            sig = hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
        elif algorithm == "sha512":
            sig = hmac.new(key.encode(), data.encode(), hashlib.sha512).hexdigest()
        else:
            sig = hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
        return HashResult(digest=sig, algorithm=f"hmac_{algorithm}", hex_digest=sig)

    def hmac_verify(self, data: str, key: str, signature: str, algorithm: str = "sha256") -> bool:
        result = self.hmac_sign(data, key, algorithm)
        return hmac.compare_digest(result.hex_digest, signature)

    def generate_salt(self, salt_id: str, size: int = 16) -> str:
        salt = secrets.token_bytes(size)
        self.salt_store[salt_id] = salt
        return salt.hex()

    def password_hash(self, password: str, iterations: int = 100000) -> str:
        salt = secrets.token_bytes(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
        return salt.hex() + ":" + h.hex()

    def password_verify(self, password: str, stored: str) -> bool:
        salt_hex, hash_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return h.hex() == hash_hex

    def count(self) -> int:
        return len(self.salt_store)
