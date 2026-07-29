"""
Encryption Manager - Handles encryption
"""

import base64
import hashlib
import hmac
import secrets
from typing import Optional, Dict

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """Manages encryption"""

    def __init__(self, config):
        self.config = config
        self._key = None
        self._fernet = None

    async def initialize(self) -> None:
        if self.config.encryption_key:
            self._key = base64.urlsafe_b64decode(self.config.encryption_key)
        else:
            self._key = Fernet.generate_key()
        self._fernet = Fernet(self._key)

    async def shutdown(self) -> None:
        pass

    async def encrypt(self, data: str, context: Optional[dict] = None) -> str:
        return self._fernet.encrypt(data.encode()).decode()

    async def decrypt(self, encrypted: str, context: Optional[dict] = None) -> str:
        return self._fernet.decrypt(encrypted.encode()).decode()

    async def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return f"{base64.b64encode(salt).decode()}:{key.decode()}"

    async def verify_password(self, password: str, hashed: str) -> bool:
        salt_b64, key_b64 = hashed.split(":")
        salt = base64.b64decode(salt_b64)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        derived = base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()
        return hmac.compare_digest(derived, key_b64)

    async def rotate_keys(self) -> None:
        old_fernet = self._fernet
        self._key = Fernet.generate_key()
        self._fernet = Fernet(self._key)

    def get_stats(self) -> Dict:
        return {"encryption_enabled": self.config.encryption_enabled}