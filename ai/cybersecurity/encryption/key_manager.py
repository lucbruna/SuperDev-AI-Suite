"""
Key Management Service
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import secrets


class KeyState(Enum):
    ACTIVE = "active"
    ROTATING = "rotating"
    DISABLED = "disabled"
    DESTROYED = "destroyed"


class KeyType(Enum):
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    WRAPPING = "wrapping"
    SIGNING = "signing"


@dataclass
class ManagedKey:
    key_id: str
    key_type: KeyType
    state: KeyState = KeyState.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    rotation_interval_days: int = 90
    usage_count: int = 0
    max_usage: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class KeyManager:
    def __init__(self):
        self.keys: Dict[str, ManagedKey] = {}
        self.key_material: Dict[str, bytes] = {}

    def create_key(self, key_id: str, key_type: KeyType = KeyType.SYMMETRIC, **kwargs) -> ManagedKey:
        key = ManagedKey(key_id=key_id, key_type=key_type, **kwargs)
        self.keys[key_id] = key
        self.key_material[key_id] = secrets.token_bytes(32)
        return key

    def get_key(self, key_id: str) -> Optional[ManagedKey]:
        return self.keys.get(key_id)

    def disable_key(self, key_id: str) -> bool:
        key = self.keys.get(key_id)
        if key:
            key.state = KeyState.DISABLED
            return True
        return False

    def destroy_key(self, key_id: str) -> bool:
        key = self.keys.get(key_id)
        if key:
            key.state = KeyState.DESTROYED
            self.key_material.pop(key_id, None)
            return True
        return False

    def rotate_key(self, key_id: str) -> Optional[ManagedKey]:
        key = self.keys.get(key_id)
        if key:
            key.state = KeyState.ROTATING
            self.key_material[key_id] = secrets.token_bytes(32)
            key.state = KeyState.ACTIVE
            key.created_at = datetime.now()
            key.usage_count = 0
            return key
        return None

    def get_keys_by_type(self, key_type: KeyType) -> List[ManagedKey]:
        return [k for k in self.keys.values() if k.key_type == key_type]

    def get_expiring_keys(self, days: int = 30) -> List[ManagedKey]:
        threshold = datetime.now() + timedelta(days=days)
        return [k for k in self.keys.values() if k.expires_at and k.expires_at <= threshold]

    def is_key_usable(self, key_id: str) -> bool:
        key = self.keys.get(key_id)
        if not key or key.state != KeyState.ACTIVE:
            return False
        if key.max_usage > 0 and key.usage_count >= key.max_usage:
            return False
        return True

    def record_usage(self, key_id: str) -> None:
        key = self.keys.get(key_id)
        if key:
            key.usage_count += 1

    def count(self) -> int:
        return len(self.keys)
