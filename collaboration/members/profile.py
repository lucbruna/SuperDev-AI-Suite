"""Member profiles."""

from __future__ import annotations

from typing import Any


class Profile:
    """Profile of a human or AI member."""

    def __init__(self, member_id: str, display_name: str,
                 bio: str = "", avatar: str = "",
                 location: str = "", extra: dict[str, Any] | None = None) -> None:
        self.member_id = member_id
        self.display_name = display_name
        self.bio = bio
        self.avatar = avatar
        self.location = location
        self.extra = dict(extra or {})

    def update(self, **fields: Any) -> None:
        for key, value in fields.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra[key] = value

    def to_dict(self) -> dict[str, Any]:
        return {"member_id": self.member_id,
                "display_name": self.display_name, "bio": self.bio,
                "avatar": self.avatar, "location": self.location,
                "extra": dict(self.extra)}


class ProfileManager:
    """Stores and retrieves member profiles."""

    def __init__(self) -> None:
        self._profiles: dict[str, Profile] = {}

    def create(self, member_id: str, display_name: str,
               bio: str = "", avatar: str = "",
               location: str = "") -> Profile:
        profile = Profile(member_id, display_name, bio, avatar, location)
        self._profiles[member_id] = profile
        return profile

    def get(self, member_id: str) -> Profile | None:
        return self._profiles.get(member_id)

    def update(self, member_id: str, **fields: Any) -> Profile | None:
        profile = self.get(member_id)
        if profile is None:
            return None
        profile.update(**fields)
        return profile

    def remove(self, member_id: str) -> bool:
        return self._profiles.pop(member_id, None) is not None
