"""Key management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import secrets, time

class KeyEntry:
    def __init__(self, key_id: str, key_material: bytes, purpose: str = "", expiry: float = 0.0) -> None:
        self.key_id = key_id
        self.key_material = key_material
        self.purpose = purpose
        self.created_at = time.time()
        self.expiry = expiry or (time.time() + 86400 * 30)
        self.active = True

class KeyManager:
    def __init__(self) -> None:
        self._keys: Dict[str, KeyEntry] = {}
        self._rotation_policy_days = 90
    def generate_key(self, key_id: str, size: int = 32, purpose: str = "") -> KeyEntry:
        entry = KeyEntry(key_id, secrets.token_bytes(size), purpose)
        self._keys[key_id] = entry
        return entry
    def get_key(self, key_id: str) -> Optional[KeyEntry]:
        entry = self._keys.get(key_id)
        if entry and entry.active and entry.expiry > time.time():
            return entry
        return None
    def revoke_key(self, key_id: str) -> bool:
        if key_id in self._keys:
            self._keys[key_id].active = False
            return True
        return False
    def rotate_key(self, old_key_id: str, new_key_id: str) -> Optional[KeyEntry]:
        old = self._keys.get(old_key_id)
        if old:
            old.active = False
            return self.generate_key(new_key_id, len(old.key_material), old.purpose)
        return None
    def list_active_keys(self) -> List[str]:
        return [k for k, v in self._keys.items() if v.active and v.expiry > time.time()]
    def list_expired_keys(self) -> List[str]:
        return [k for k, v in self._keys.items() if v.expiry <= time.time()]
    def cleanup_expired(self) -> int:
        expired = self.list_expired_keys()
        for k in expired:
            self.revoke_key(k)
        return len(expired)
