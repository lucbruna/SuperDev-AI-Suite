"""
User Identity
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserIdentity:
    user_id: str
    username: str
    email: str
    display_name: str = ""
    avatar_url: str = ""
    phone: str = ""
    timezone: str = "UTC"
    locale: str = "en"
    preferences: dict[str, Any] = field(default_factory=dict)
    last_login: datetime | None = None
    is_verified: bool = False

    @property
    def full_name(self) -> str:
        return self.display_name or self.username


class UserIdentityManager:
    def __init__(self):
        self.users: dict[str, UserIdentity] = {}

    def create_user(self, user_id: str, username: str, email: str, **kwargs) -> UserIdentity:
        user = UserIdentity(user_id=user_id, username=username, email=email, **kwargs)
        self.users[user_id] = user
        return user

    def get_user(self, user_id: str) -> UserIdentity | None:
        return self.users.get(user_id)

    def update_user(self, user_id: str, **kwargs) -> bool:
        user = self.get_user(user_id)
        if user:
            for k, v in kwargs.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            return True
        return False

    def delete_user(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    def find_by_email(self, email: str) -> UserIdentity | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def find_by_username(self, username: str) -> UserIdentity | None:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def count(self) -> int:
        return len(self.users)
