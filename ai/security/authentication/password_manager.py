"""Password management and hashing."""
from __future__ import annotations
from typing import Any, Dict
import hashlib, secrets, time

class PasswordManager:
    def __init__(self) -> None:
        self._history: Dict[str, list[str]] = {}
    def hash_password(self, password: str, salt: str = "") -> str:
        s = salt or secrets.token_hex(16)
        return hashlib.sha256((password + s).encode()).hexdigest() + ":" + s
    def verify_password(self, password: str, stored_hash: str) -> bool:
        if ":" not in stored_hash:
            return False
        hash_part, salt = stored_hash.rsplit(":", 1)
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_part
    def validate_strength(self, password: str) -> Dict[str, Any]:
        issues = []
        if len(password) < 12: issues.append("too_short")
        if not any(c.isupper() for c in password): issues.append("no_uppercase")
        if not any(c.islower() for c in password): issues.append("no_lowercase")
        if not any(c.isdigit() for c in password): issues.append("no_digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): issues.append("no_special")
        return {"strong": len(issues) == 0, "issues": issues}
    def check_reuse(self, user_id: str, new_password: str) -> bool:
        history = self._history.get(user_id, [])
        for h in history:
            if self.verify_password(new_password, h):
                return True
        return False
