"""
Secret Storage and Management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import secrets
import hashlib


class SecretType(Enum):
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    DATABASE_URL = "database_url"


class SecretState(Enum):
    ACTIVE = "active"
    ROTATED = "rotated"
    DISABLED = "disabled"
    DELETED = "deleted"


@dataclass
class Secret:
    secret_id: str
    name: str
    secret_type: SecretType
    value_hash: str = ""
    state: SecretState = SecretState.ACTIVE
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    rotated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecretManager:
    def __init__(self):
        self.secrets: Dict[str, Secret] = {}
        self.secret_values: Dict[str, str] = {}
        self.access_log: list = []

    def create_secret(self, name: str, value: str, secret_type: SecretType = SecretType.API_KEY) -> Secret:
        secret_id = secrets.token_hex(16)
        val_hash = hashlib.sha256(value.encode()).hexdigest()
        secret = Secret(secret_id=secret_id, name=name, secret_type=secret_type, value_hash=val_hash)
        self.secrets[secret_id] = secret
        self.secret_values[secret_id] = value
        return secret

    def get_secret(self, secret_id: str, accessor: str = "system") -> Optional[str]:
        secret = self.secrets.get(secret_id)
        if not secret or secret.state != SecretState.ACTIVE:
            return None
        secret.access_count += 1
        self.access_log.append({"secret_id": secret_id, "accessor": accessor, "time": datetime.now().isoformat()})
        return self.secret_values.get(secret_id)

    def rotate_secret(self, secret_id: str, new_value: str) -> Optional[Secret]:
        secret = self.secrets.get(secret_id)
        if secret:
            secret.version += 1
            secret.rotated_at = datetime.now()
            secret.value_hash = hashlib.sha256(new_value.encode()).hexdigest()
            self.secret_values[secret_id] = new_value
            return secret
        return None

    def delete_secret(self, secret_id: str) -> bool:
        secret = self.secrets.get(secret_id)
        if secret:
            secret.state = SecretState.DELETED
            self.secret_values.pop(secret_id, None)
            return True
        return False

    def find_by_name(self, name: str) -> List[Secret]:
        return [s for s in self.secrets.values() if s.name == name]

    def find_by_type(self, secret_type: SecretType) -> List[Secret]:
        return [s for s in self.secrets.values() if s.secret_type == secret_type]

    def list_active(self) -> List[Secret]:
        return [s for s in self.secrets.values() if s.state == SecretState.ACTIVE]

    def count(self) -> int:
        return len(self.secrets)
