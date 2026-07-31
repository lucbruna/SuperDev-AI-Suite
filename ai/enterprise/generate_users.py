"""Users subsystem generator."""
import os

BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\enterprise\users'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('user_engine.py', '''"""User engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class UserEngine:
    def __init__(self) -> None:
        self._users: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def create(self, email: str, name: str, org_id: str = "", role: str = "member") -> Dict[str, Any]:
        import uuid
        user_id = str(uuid.uuid4())[:8]
        user = {"id": user_id, "email": email, "name": name, "org_id": org_id, "role": role, "status": "active", "created_at": time.time()}
        self._users[user_id] = user
        return user
    def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for u in self._users.values():
            if u.get("email") == email:
                return u
        return None
    def update(self, user_id: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        user = self._users.get(user_id)
        if user:
            user.update(kwargs)
            return user
        return None
    def delete(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._users.values())
    def list_by_org(self, org_id: str) -> List[Dict[str, Any]]:
        return [u for u in self._users.values() if u.get("org_id") == org_id]
    def count(self) -> int:
        return len(self._users)
''')

w('user_manager.py', '''"""User manager."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class UserManager:
    def __init__(self) -> None:
        self._roles: Dict[str, List[str]] = {"admin": ["*"], "manager": ["read", "write", "manage"], "member": ["read", "write"], "viewer": ["read"]}
        self._assignments: Dict[str, str] = {}
    def assign_role(self, user_id: str, role: str) -> bool:
        self._assignments[user_id] = role
        return True
    def get_role(self, user_id: str) -> str:
        return self._assignments.get(user_id, "viewer")
    def has_permission(self, user_id: str, permission: str) -> bool:
        role = self.get_role(user_id)
        perms = self._roles.get(role, [])
        return "*" in perms or permission in perms
    def list_roles(self) -> Dict[str, List[str]]:
        return dict(self._roles)
    def add_role(self, name: str, permissions: List[str]) -> None:
        self._roles[name] = permissions
    def remove_role(self, name: str) -> bool:
        if name in self._roles and name not in ("admin", "viewer"):
            del self._roles[name]
            return True
        return False
    def list_users_by_role(self, role: str) -> List[str]:
        return [uid for uid, r in self._assignments.items() if r == role]
''')

w('profile.py', '''"""User profile."""
from __future__ import annotations
from typing import Any, Dict, Optional

class UserProfile:
    def __init__(self) -> None:
        self._profiles: Dict[str, Dict[str, Any]] = {}
    def create(self, user_id: str, display_name: str = "", avatar_url: str = "", bio: str = "") -> Dict[str, Any]:
        profile = {"user_id": user_id, "display_name": display_name, "avatar_url": avatar_url, "bio": bio, "phone": "", "location": "", "timezone": "America/Sao_Paulo"}
        self._profiles[user_id] = profile
        return profile
    def get(self, user_id: str) -> Dict[str, Any]:
        return self._profiles.get(user_id, {})
    def update(self, user_id: str, **kwargs: Any) -> Dict[str, Any]:
        if user_id in self._profiles:
            self._profiles[user_id].update(kwargs)
            return self._profiles[user_id]
        return self.create(user_id, **kwargs)
    def delete(self, user_id: str) -> bool:
        if user_id in self._profiles:
            del self._profiles[user_id]
            return True
        return False
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._profiles)
''')

w('invitation.py', '''"""User invitations."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class InvitationManager:
    def __init__(self) -> None:
        self._invitations: Dict[str, Dict[str, Any]] = {}
    def create(self, email: str, org_id: str, role: str = "member", invited_by: str = "") -> Dict[str, Any]:
        inv_id = str(uuid.uuid4())[:8]
        inv = {"id": inv_id, "email": email, "org_id": org_id, "role": role, "invited_by": invited_by, "status": "pending", "created_at": time.time(), "expires_at": time.time() + 7*86400}
        self._invitations[inv_id] = inv
        return inv
    def get(self, inv_id: str) -> Optional[Dict[str, Any]]:
        return self._invitations.get(inv_id)
    def accept(self, inv_id: str) -> bool:
        inv = self._invitations.get(inv_id)
        if inv and inv["status"] == "pending":
            inv["status"] = "accepted"
            inv["accepted_at"] = time.time()
            return True
        return False
    def decline(self, inv_id: str) -> bool:
        inv = self._invitations.get(inv_id)
        if inv and inv["status"] == "pending":
            inv["status"] = "declined"
            return True
        return False
    def revoke(self, inv_id: str) -> bool:
        inv = self._invitations.get(inv_id)
        if inv:
            inv["status"] = "revoked"
            return True
        return False
    def list_pending(self, org_id: str = "") -> List[Dict[str, Any]]:
        results = [i for i in self._invitations.values() if i["status"] == "pending"]
        if org_id:
            results = [i for i in results if i["org_id"] == org_id]
        return results
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._invitations.values())
''')

w('status.py', '''"""User status."""
from __future__ import annotations
from typing import Any, Dict

class UserStatusManager:
    def __init__(self) -> None:
        self._statuses: Dict[str, str] = {}
    def activate(self, user_id: str) -> bool:
        self._statuses[user_id] = "active"
        return True
    def deactivate(self, user_id: str) -> bool:
        self._statuses[user_id] = "inactive"
        return True
    def suspend(self, user_id: str, reason: str = "") -> bool:
        self._statuses[user_id] = "suspended"
        return True
    def get_status(self, user_id: str) -> str:
        return self._statuses.get(user_id, "active")
    def is_active(self, user_id: str) -> bool:
        return self.get_status(user_id) == "active"
    def list_by_status(self, status: str) -> list:
        return [uid for uid, s in self._statuses.items() if s == status]
    def bulk_update(self, user_ids: list, status: str) -> int:
        count = 0
        for uid in user_ids:
            self._statuses[uid] = status
            count += 1
        return count
''')

w('activity.py', '''"""User activity."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class UserActivity:
    def __init__(self) -> None:
        self._activities: Dict[str, List[Dict[str, Any]]] = {}
    def log(self, user_id: str, action: str, resource: str = "", details: str = "") -> Dict[str, Any]:
        entry = {"action": action, "resource": resource, "details": details, "timestamp": time.time()}
        self._activities.setdefault(user_id, []).append(entry)
        return entry
    def get_activities(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return self._activities.get(user_id, [])[-limit:]
    def get_last_activity(self, user_id: str) -> Dict[str, Any]:
        activities = self._activities.get(user_id, [])
        return activities[-1] if activities else {}
    def count(self, user_id: str) -> int:
        return len(self._activities.get(user_id, []))
    def clear(self, user_id: str) -> int:
        n = len(self._activities.get(user_id, []))
        self._activities.pop(user_id, None)
        return n
    def get_active_users(self, hours: int = 24) -> List[str]:
        cutoff = time.time() - hours * 3600
        active = []
        for user_id, activities in self._activities.items():
            if activities and activities[-1]["timestamp"] > cutoff:
                active.append(user_id)
        return active
''')

w('preferences.py', '''"""User preferences."""
from __future__ import annotations
from typing import Any, Dict

class UserPreferences:
    DEFAULTS = {"theme": "light", "language": "pt-BR", "notifications_email": True, "notifications_push": True, "dashboard_layout": "default"}
    def __init__(self) -> None:
        self._prefs: Dict[str, Dict[str, Any]] = {}
    def get(self, user_id: str) -> Dict[str, Any]:
        return {**self.DEFAULTS, **self._prefs.get(user_id, {})}
    def set(self, user_id: str, key: str, value: Any) -> None:
        self._prefs.setdefault(user_id, {})[key] = value
    def set_many(self, user_id: str, values: Dict[str, Any]) -> None:
        self._prefs.setdefault(user_id, {}).update(values)
    def get_one(self, user_id: str, key: str) -> Any:
        return self._prefs.get(user_id, {}).get(key, self.DEFAULTS.get(key))
    def reset(self, user_id: str, key: str) -> bool:
        if user_id in self._prefs and key in self._prefs[user_id]:
            del self._prefs[user_id][key]
            return True
        return False
    def reset_all(self, user_id: str) -> int:
        n = len(self._prefs.get(user_id, {}))
        self._prefs.pop(user_id, None)
        return n
''')

w('__init__.py', '''"""Users subsystem."""
from .user_engine import UserEngine
from .user_manager import UserManager
from .profile import UserProfile
from .invitation import InvitationManager
from .status import UserStatusManager
from .activity import UserActivity
from .preferences import UserPreferences

__all__ = [
    "UserEngine", "UserManager", "UserProfile", "InvitationManager",
    "UserStatusManager", "UserActivity", "UserPreferences"
]
''')

print("users/: 8 files created")
