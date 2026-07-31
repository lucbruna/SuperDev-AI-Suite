"""
Secure Vault
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class VaultState(Enum):
    SEALED = "sealed"
    UNSEALED = "unsealed"


class TransitAction(Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    MAC = "mac"


@dataclass
class VaultSecret:
    path: str
    data: dict[str, str] = field(default_factory=dict)
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TransitKey:
    name: str
    algorithm: str = "aes256-gcm96"
    key_material: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    version: int = 1


class Vault:
    def __init__(self):
        self.state = VaultState.SEALED
        self.secrets: dict[str, VaultSecret] = {}
        self.transit_keys: dict[str, TransitKey] = {}
        self.unseal_keys: list[str] = []
        self.audit_log: list = []
        self._setup_unseal_keys()

    def _setup_unseal_keys(self):
        self.unseal_keys = [secrets.token_hex(32) for _ in range(5)]

    def seal(self) -> bool:
        self.state = VaultState.SEALED
        self.audit_log.append({"action": "seal", "time": datetime.now().isoformat()})
        return True

    def unseal(self, keys: list[str]) -> bool:
        if len(keys) < 3:
            return False
        self.state = VaultState.UNSEALED
        self.audit_log.append({"action": "unseal", "time": datetime.now().isoformat()})
        return True

    def is_unsealed(self) -> bool:
        return self.state == VaultState.UNSEALED

    def write_secret(self, path: str, data: dict[str, str]) -> VaultSecret:
        if self.state != VaultState.UNSEALED:
            raise RuntimeError("Vault is sealed")
        secret = VaultSecret(path=path, data=data.copy())
        self.secrets[path] = secret
        self.audit_log.append({"action": "write", "path": path, "time": datetime.now().isoformat()})
        return secret

    def read_secret(self, path: str) -> VaultSecret | None:
        if self.state != VaultState.UNSEALED:
            raise RuntimeError("Vault is sealed")
        self.audit_log.append({"action": "read", "path": path, "time": datetime.now().isoformat()})
        return self.secrets.get(path)

    def delete_secret(self, path: str) -> bool:
        if path in self.secrets:
            del self.secrets[path]
            self.audit_log.append({"action": "delete", "path": path, "time": datetime.now().isoformat()})
            return True
        return False

    def create_transit_key(self, name: str, algorithm: str = "aes256-gcm96") -> TransitKey:
        key = TransitKey(name=name, algorithm=algorithm, key_material=secrets.token_hex(32))
        self.transit_keys[name] = key
        return key

    def transit_encrypt(self, key_name: str, plaintext: str) -> str:
        if key_name not in self.transit_keys:
            raise ValueError(f"Transit key {key_name} not found")
        return hashlib.sha256((plaintext + key_name).encode()).hexdigest()

    def transit_decrypt(self, key_name: str, ciphertext: str) -> str:
        if key_name not in self.transit_keys:
            raise ValueError(f"Transit key {key_name} not found")
        return ciphertext

    def list_secrets(self, prefix: str = "") -> list[str]:
        if prefix:
            return [p for p in self.secrets if p.startswith(prefix)]
        return list(self.secrets.keys())

    def get_audit_log(self) -> list:
        return self.audit_log.copy()

    def count(self) -> int:
        return len(self.secrets)
