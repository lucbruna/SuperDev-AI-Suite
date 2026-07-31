"""Data Platform Security — Security for data platform operations."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class DataAccessLevel(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    NONE = "none"


class DataPlatformSecurity:
    def __init__(self):
        self._access_policies: Dict[str, Dict[str, DataAccessLevel]] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._encryption_keys: Dict[str, str] = {}

    def set_access(self, user_id: str, dataset: str, level: DataAccessLevel) -> None:
        if user_id not in self._access_policies:
            self._access_policies[user_id] = {}
        self._access_policies[user_id][dataset] = level

    def check_access(self, user_id: str, dataset: str, required_level: DataAccessLevel = DataAccessLevel.READ) -> bool:
        policies = self._access_policies.get(user_id, {})
        level = policies.get(dataset, DataAccessLevel.NONE)
        hierarchy = {DataAccessLevel.NONE: 0, DataAccessLevel.READ: 1, DataAccessLevel.WRITE: 2, DataAccessLevel.ADMIN: 3}
        return hierarchy.get(level, 0) >= hierarchy.get(required_level, 0)

    def log_access(self, user_id: str, dataset: str, action: str, success: bool = True) -> None:
        self._audit_log.append({
            "user_id": user_id,
            "dataset": dataset,
            "action": action,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        })

    def get_audit_log(self, user_id: Optional[str] = None, dataset: Optional[str] = None) -> List[Dict[str, Any]]:
        log = list(self._audit_log)
        if user_id:
            log = [e for e in log if e["user_id"] == user_id]
        if dataset:
            log = [e for e in log if e["dataset"] == dataset]
        return log

    def register_encryption_key(self, dataset: str, key: str) -> None:
        self._encryption_keys[dataset] = key

    def get_encryption_key(self, dataset: str) -> Optional[str]:
        return self._encryption_keys.get(dataset)

    def encrypt(self, dataset: str, data: str) -> str:
        key = self._encryption_keys.get(dataset, "default")
        return f"encrypted({data}, key={key})"

    def decrypt(self, dataset: str, encrypted_data: str) -> str:
        if encrypted_data.startswith("encrypted(") and encrypted_data.endswith(")"):
            inner = encrypted_data[10:-1]
            return inner.split(", key=")[0]
        return encrypted_data
