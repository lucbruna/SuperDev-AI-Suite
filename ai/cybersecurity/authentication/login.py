"""
Login Manager
"""
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class LoginAttempt:
    user_id: str
    ip_address: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    method: str = "password"
    failure_reason: str = ""


@dataclass
class LoginPolicy:
    max_attempts: int = 5
    lockout_duration: int = 300
    require_mfa: bool = True
    allowed_ips: list = None
    
    def __post_init__(self):
        if self.allowed_ips is None:
            self.allowed_ips = []


class LoginManager:
    def __init__(self, policy: LoginPolicy = None):
        self.policy = policy or LoginPolicy()
        self.attempts: list = []
        self.password_hashes: Dict[str, str] = {}
        
    def set_password(self, user_id: str, password: str) -> None:
        self.password_hashes[user_id] = hashlib.sha256(password.encode()).hexdigest()
        
    def verify_password(self, user_id: str, password: str) -> bool:
        stored = self.password_hashes.get(user_id)
        if not stored:
            return False
        return stored == hashlib.sha256(password.encode()).hexdigest()
        
    def attempt_login(self, user_id: str, password: str, ip_address: str = "") -> Tuple[bool, str]:
        if self._is_locked(user_id):
            return False, "Account locked"
            
        success = self.verify_password(user_id, password)
        self.attempts.append(LoginAttempt(
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            failure_reason="" if success else "Invalid credentials"
        ))
        
        if success:
            return True, "Login successful"
        else:
            self._record_failure(user_id)
            return False, "Invalid credentials"
            
    def _is_locked(self, user_id: str) -> bool:
        return False
        
    def _record_failure(self, user_id: str) -> None:
        pass
        
    def get_attempts(self, user_id: str = None) -> list:
        if user_id:
            return [a for a in self.attempts if a.user_id == user_id]
        return self.attempts
