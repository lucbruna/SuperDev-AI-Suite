"""Identity and access management engine."""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


class AccessLevel(Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


class AuthStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"
    MFA_REQUIRED = "mfa_required"


@dataclass
class IdentityUser:
    user_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    username: str = ""
    email: str = ""
    role: str = "viewer"
    permissions: List[AccessLevel] = field(default_factory=list)
    is_active: bool = True
    mfa_enabled: bool = False
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Permission:
    permission_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    resource: str = ""
    access_level: AccessLevel = AccessLevel.READ
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthLog:
    log_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    username: str = ""
    status: AuthStatus = AuthStatus.SUCCESS
    ip_address: str = ""
    mfa_used: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class IdentityEngine:
    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 30):
        self._users: Dict[str, IdentityUser] = {}
        self._roles: Dict[str, List[Permission]] = {}
        self._auth_log: List[AuthLog] = []
        self._max_attempts = max_attempts
        self._lockout_minutes = lockout_minutes

    def create_user(self, user: IdentityUser) -> IdentityUser:
        self._users[user.user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[IdentityUser]:
        return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[IdentityUser]:
        for u in self._users.values():
            if u.username == username:
                return u
        return None

    def authenticate(self, username: str, password: str, ip_address: str = "") -> AuthStatus:
        user = self.get_user_by_username(username)
        if not user:
            self._auth_log.append(AuthLog(username=username, status=AuthStatus.FAILED, ip_address=ip_address))
            return AuthStatus.FAILED
        if user.locked_until and user.locked_until > datetime.now():
            return AuthStatus.LOCKED
        if not user.is_active:
            return AuthStatus.FAILED
        user.failed_attempts += 1
        if user.failed_attempts >= self._max_attempts:
            from datetime import timedelta
            user.locked_until = datetime.now() + timedelta(minutes=self._lockout_minutes)
            self._auth_log.append(AuthLog(user_id=user.user_id, username=username, status=AuthStatus.LOCKED, ip_address=ip_address))
            return AuthStatus.LOCKED
        user.last_login = datetime.now()
        self._auth_log.append(AuthLog(user_id=user.user_id, username=username, status=AuthStatus.SUCCESS, ip_address=ip_address))
        if user.mfa_enabled:
            return AuthStatus.MFA_REQUIRED
        return AuthStatus.SUCCESS

    def authorize(self, user_id: str, resource: str, required_level: AccessLevel) -> bool:
        user = self._users.get(user_id)
        if not user or not user.is_active:
            return False
        if user.role == "admin":
            return True
        role_perms = self._roles.get(user.role, [])
        for perm in role_perms:
            if perm.resource == resource and perm.access_level.value >= required_level.value:
                return True
        return False

    def set_role_permissions(self, role: str, permissions: List[Permission]) -> None:
        self._roles[role] = permissions

    def lock_user(self, user_id: str) -> bool:
        user = self._users.get(user_id)
        if not user:
            return False
        from datetime import timedelta
        user.locked_until = datetime.now() + timedelta(minutes=self._lockout_minutes)
        return True

    def unlock_user(self, user_id: str) -> bool:
        user = self._users.get(user_id)
        if not user:
            return False
        user.locked_until = None
        user.failed_attempts = 0
        return True

    def get_auth_log(self, user_id: Optional[str] = None) -> List[AuthLog]:
        log = list(self._auth_log)
        if user_id:
            log = [e for e in log if e.user_id == user_id]
        return log

    def get_stats(self) -> dict:
        users = list(self._users.values())
        return {
            "total_users": len(users),
            "active": len([u for u in users if u.is_active]),
            "locked": len([u for u in users if u.locked_until and u.locked_until > datetime.now()]),
            "mfa_enabled": len([u for u in users if u.mfa_enabled]),
            "auth_attempts": len(self._auth_log),
            "failed_attempts": len([e for e in self._auth_log if e.status == AuthStatus.FAILED]),
        }
